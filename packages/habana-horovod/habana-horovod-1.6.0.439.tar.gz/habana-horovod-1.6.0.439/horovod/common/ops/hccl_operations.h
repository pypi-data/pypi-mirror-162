// Copyright 2016 The TensorFlow Authors. All Rights Reserved.
// Modifications copyright (C) 2019 Uber Technologies, Inc.
// Modifications copyright (C) 2020, NVIDIA CORPORATION. All rights reserved.
// Modifications copyright (C) 2021, Intel Corporation. All rights reserved.
//
// Licensed under the Apache License, Version 2.0 (the "License");
// you may not use this file except in compliance with the License.
// You may obtain a copy of the License at
//
//     http://www.apache.org/licenses/LICENSE-2.0
//
// Unless required by applicable law or agreed to in writing, software
// distributed under the License is distributed on an "AS IS" BASIS,
// WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
// See the License for the specific language governing permissions and
// limitations under the License.
// =============================================================================

#ifndef HOROVOD_HCCL_OPERATIONS_H
#define HOROVOD_HCCL_OPERATIONS_H

#if HAVE_HCCL

#include <hccl.h>
#include <map>
#include <mutex>
#include <set>
#include <synapse_api.h>
#include <thread>
#include <vector>
#define HCCL_P2P_SUPPORTED 1

#include "../thread_pool.h"
#include "collective_operations.h"

#if HAVE_MPI
#include "../mpi/mpi_context.h"
#endif

#include <functional>

#define hcclStream_t synStreamHandle

#define HCCL_OP_ASSERT(condition)                                              \
  {                                                                            \
    if (!(condition)) {                                                        \
      LOG(FATAL) << "Assertion failed! [" << #condition << "] @" << __FILE__   \
                 << "::" << __LINE__;                                          \
    }                                                                          \
  }

#define HCCL_OP_CHECK_ERROR(_status, _msg)                                     \
  {                                                                            \
    if (hcclSuccess != (_status)) {                                            \
      LOG(FATAL) << (_msgs) << " Status: " << _status << "@" << __FILE__       \
                 << "::" << __LINE__                                           \
    }                                                                          \
  }

#define SYNC_AFTER_HCCL_IF_NEED(op_ctx)                                        \
  if (ShouldSynchronizeAfterHccl()) {                                          \
    (op_ctx).SynchronizeCurrentStream();                                       \
  }

namespace horovod {
namespace common {

hcclDataType_t GetHCCLDataType(const DataType data_type);

class HPUDeviceContext {
public:
  HPUDeviceContext(int device_id);
  ~HPUDeviceContext();

  int device_id() const { return device_id_; }
  synStreamHandle collective_stream();
  synStreamHandle d2h_stream();
  synStreamHandle h2d_stream();
  synStreamHandle d2d_stream();
  void release_collective_stream();

private:
  void release_copy_streams();

private:
  int device_id_;
  synStreamHandle collective_stream_ = nullptr;
  synStreamHandle d2h_stream_ = nullptr;
  synStreamHandle h2d_stream_ = nullptr;
  synStreamHandle d2d_stream_ = nullptr;
};

struct HCCLContext {
  std::unordered_map<std::vector<int32_t>, hcclComm_t> hccl_comms;
  ThreadPool finalizer_thread_pool;
  const int THREADS_IN_FINALIZER_POOL = 1;

  HCCLContext() { finalizer_thread_pool.create(THREADS_IN_FINALIZER_POOL); }
  void ErrorCheck(std::string op_name, hcclResult_t hccl_result,
                  hcclComm_t& hccl_comm);

  HPUDeviceContext* OpenDevice(int device_id);

  void SetDevice(int device_id);

  void ShutDown();

  void hvd_global_ptr(HorovodGlobalState* ptr) {
    if (ptr == nullptr)

      throw std::logic_error("HCCLContext::hvd_global_ptr() failed: "
                             "HorovodGlobalState* ptr cannot be null.");
    hvd_global_ptr_ = ptr;
  }

  bool IsDeviceOpen(int device_id) {
    bool entry_exists{opened_devices_.end() != opened_devices_.find(device_id)};
    return entry_exists ? (opened_devices_.at(device_id) != nullptr) : false;
  }

private:
  std::unordered_map<int, std::unique_ptr<HPUDeviceContext>> opened_devices_;
  HorovodGlobalState* hvd_global_ptr_{nullptr};
};

class HCCLOpContext {

public:
  HCCLOpContext(HCCLContext* hccl_context, HorovodGlobalState* global_state,
                horovod::common::Communicator communicator_type)
      : hccl_comm_(nullptr), hccl_context_(hccl_context),
        global_state_(global_state), communicator_type_(communicator_type){};

  void InitCommunicator(const std::vector<TensorTableEntry>& entries,
                        const std::vector<int32_t>& hccl_device_map);
  void InitDeviceQueue(const std::vector<TensorTableEntry>& entries,
                       synStreamHandle initial_stream);

  Status FinalizeDeviceQueue(std::vector<TensorTableEntry>& entries,
                             std::function<void()> on_finalize = {});

  void SynchronizeCurrentStream();

  hcclComm_t* hccl_comm_;

  void CopyDataToDevice(const void* src, void* dst, size_t size);
  void CopyDataToHost(void* src, void* dst, size_t size);

  synStreamHandle host_to_device_copy_stream();
  synStreamHandle device_to_host_copy_stream();
  synStreamHandle within_device_copy_stream();
  synStreamHandle collective_stream();

private:
  void SwitchStreams(synStreamHandle next_stream);

  synStreamHandle current_stream() const {
    // TODO: rewrite
    HCCL_OP_ASSERT(nullptr != current_stream_);
    return current_stream_;
  }

  HPUDeviceContext* my_device_{nullptr};
  HCCLContext* hccl_context_;
  HorovodGlobalState* global_state_;
  synStreamHandle current_stream_{nullptr};
  horovod::common::Communicator communicator_type_;
};

inline void HCCLOpContext::SynchronizeCurrentStream() {
  HCCL_OP_ASSERT(my_device_ != nullptr);
  const synStreamHandle stream_to_synchronize{current_stream_};
  if (stream_to_synchronize) {
    synStatus status{synSuccess};
    synEventHandle event_handle;

    status = synEventCreate(&event_handle, my_device_->device_id(), 0);
    HCCL_OP_ASSERT(synSuccess == status);
    status = synEventRecord(event_handle, stream_to_synchronize);
    HCCL_OP_ASSERT(synSuccess == status);
    status = synEventSynchronize(event_handle);
    HCCL_OP_ASSERT(synSuccess == status);
    status = synEventDestroy(event_handle);
    HCCL_OP_ASSERT(synSuccess == status);
    current_stream_ = nullptr;
  }
}

inline synStreamHandle HCCLOpContext::host_to_device_copy_stream() {
  HCCL_OP_ASSERT(my_device_ != nullptr);
  SwitchStreams(my_device_->h2d_stream());
  return current_stream_;
}

inline synStreamHandle HCCLOpContext::device_to_host_copy_stream() {
  HCCL_OP_ASSERT(my_device_ != nullptr);
  SwitchStreams(my_device_->d2h_stream());
  return current_stream_;
}

inline synStreamHandle HCCLOpContext::within_device_copy_stream() {
  HCCL_OP_ASSERT(my_device_ != nullptr);
  SwitchStreams(my_device_->d2d_stream());
  return current_stream_;
}

inline synStreamHandle HCCLOpContext::collective_stream() {
  HCCL_OP_ASSERT(my_device_ != nullptr);
  SwitchStreams(my_device_->collective_stream());
  return current_stream_;
}

inline void HCCLOpContext::SwitchStreams(synStreamHandle next_stream) {
  const synStreamHandle current_stream{current_stream_};
  if (current_stream != next_stream && current_stream != nullptr) {

    synEventHandle event;
    synStatus status{synSuccess};
    HCCL_OP_ASSERT(synSuccess == status);
    status = synEventCreate(&event, my_device_->device_id(), 0);
    HCCL_OP_ASSERT(synSuccess == status);
    status = synEventRecord(event, current_stream);
    HCCL_OP_ASSERT(synSuccess == status);
    status = synStreamWaitEvent(next_stream, event, 0);
    HCCL_OP_ASSERT(synSuccess == status);
    status = synEventDestroy(event);
    HCCL_OP_ASSERT(synSuccess == status);
  }
  current_stream_ = next_stream;
}

class HCCLAllreduce : public AllreduceOp {
public:
  HCCLAllreduce(
      HCCLContext* hccl_context, HorovodGlobalState* global_state,
      horovod::common::Communicator communicator_type = Communicator::GLOBAL)
      : AllreduceOp(global_state), hccl_context_(hccl_context),
        op_context_(hccl_context, global_state, communicator_type),
        global_state_(global_state) {}

  Status Execute(std::vector<TensorTableEntry>& entries,
                 const Response& response) override;

  void MemcpyInFusionBuffer(const std::vector<TensorTableEntry>& entries,
                            const void*& fused_input_data, void*& buffer_data,
                            size_t& buffer_len) override;

  void MemcpyOutFusionBuffer(const void* buffer_data,
                             std::vector<TensorTableEntry>& entries) override;

  virtual bool Enabled(const ParameterManager& param_manager,
                       const std::vector<TensorTableEntry>& entries,
                       const Response& response) const override;

protected:
  HCCLContext* hccl_context_;
  HCCLOpContext op_context_;
  HorovodGlobalState* global_state_;
};

class HCCLDummyAllreduce : public HCCLAllreduce {
public:
  HCCLDummyAllreduce(
      HCCLContext* hccl_context, HorovodGlobalState* global_state,
      horovod::common::Communicator communicator_type = Communicator::GLOBAL)
      : HCCLAllreduce(hccl_context, global_state, communicator_type) {}

  Status Execute(std::vector<TensorTableEntry>& entries,
                 const Response& response) override;

  virtual bool Enabled(const ParameterManager& param_manager,
                       const std::vector<TensorTableEntry>& entries,
                       const Response& response) const override;
};

class HCCLReduceScatter : public ReduceScatterOp {
public:
  HCCLReduceScatter(
      HCCLContext* hccl_context, HorovodGlobalState* global_state,
      horovod::common::Communicator communicator_type = Communicator::GLOBAL)
      : ReduceScatterOp(global_state), hccl_context_(hccl_context),
        op_context_(hccl_context, global_state, communicator_type),
        global_state_(global_state) {}

  Status Execute(std::vector<TensorTableEntry>& entries,
                 const Response& response) override;

  virtual bool Enabled(const ParameterManager& param_manager,
                       const std::vector<TensorTableEntry>& entries,
                       const Response& response) const override;

protected:
  HCCLContext* hccl_context_;
  HCCLOpContext op_context_;
  HorovodGlobalState* global_state_;
};

class HCCLAlltoall : public AlltoallOp {
public:
  HCCLAlltoall(
      HCCLContext* hccl_context, HorovodGlobalState* global_state,
      horovod::common::Communicator communicator_type = Communicator::GLOBAL)
      : AlltoallOp(global_state), hccl_context_(hccl_context),
        op_context_(hccl_context, global_state, communicator_type),
        global_state_(global_state) {}

  Status Execute(std::vector<TensorTableEntry>& entries,
                 const Response& response) override;

  virtual bool Enabled(const ParameterManager& param_manager,
                       const std::vector<TensorTableEntry>& entries,
                       const Response& response) const override;

protected:
  HCCLContext* hccl_context_;
  HCCLOpContext op_context_;
  HorovodGlobalState* global_state_;
};

class HCCLAllgather : public AllgatherOp {
public:
  HCCLAllgather(HCCLContext* hccl_context, HorovodGlobalState* global_state)
      : AllgatherOp(global_state), hccl_context_(hccl_context),
        op_context_(hccl_context, global_state, Communicator::GLOBAL),
        global_state_(global_state) {}

  Status Execute(std::vector<TensorTableEntry>& entries,
                 const Response& response) override;

  bool Enabled(const ParameterManager& param_manager,
               const std::vector<TensorTableEntry>& entries,
               const Response& response) const override;

  bool SameShape(std::vector<TensorTableEntry>& entries,
                 const Response& response, int global_size);

protected:
  class FusionData {
  public:
    FusionData(int comm_size, size_t tensor_count, size_t element_size);
    ~FusionData();

    size_t GetInputOffset(int rank) {
      return displacements_[rank] * element_size_;
    }

    size_t GetRecvCount(int rank) {
      return recieve_data_counts_[rank] * element_size_ / 2;
    }

    int64_t**& entry_component_offsets() { return entry_component_offsets_; }

    int64_t**& entry_component_sizes() { return entry_component_sizes_; }

    int*& recieve_data_counts() { return recieve_data_counts_; }

    int*& displacements() { return displacements_; }

    size_t element_size() { return element_size_; }

  private:
    int64_t** entry_component_offsets_;
    int64_t** entry_component_sizes_;
    int* recieve_data_counts_;
    int* displacements_;
    size_t tensor_count_;
    size_t element_size_;
  };

  void MemcpyInFusionBuffer(const std::vector<TensorTableEntry>& entries,
                            const void*& fused_input_data, void*& buffer_data,
                            int64_t initial_offset = 0);

  void MemcpyOutFusionBuffer(void*& buffer_data,
                             const std::vector<TensorTableEntry>& entries,
                             FusionData& fusion_data);

  HCCLContext* hccl_context_;
  HCCLOpContext op_context_;
  HorovodGlobalState* global_state_;
};

class HCCLBroadcast : public BroadcastOp {
public:
  HCCLBroadcast(
      HCCLContext* hccl_context, HorovodGlobalState* global_state,
      horovod::common::Communicator communicator_type = Communicator::GLOBAL)
      : BroadcastOp(global_state), hccl_context_(hccl_context),
        op_context_(hccl_context, global_state, communicator_type),
        global_state_(global_state) {}

  Status Execute(std::vector<TensorTableEntry>& entries,
                 const Response& response) override;

  bool Enabled(const ParameterManager& param_manager,
               const std::vector<TensorTableEntry>& entries,
               const Response& response) const override;

protected:
  HCCLContext* hccl_context_;
  HCCLOpContext op_context_;
  HorovodGlobalState* global_state_;
};

#if HAVE_MPI
class HCCLHierarchicalAllreduce : public HCCLAllreduce {
public:
  HCCLHierarchicalAllreduce(HCCLContext* hccl_context, MPIContext* mpi_context,
                            HorovodGlobalState* global_state)
      : HCCLAllreduce(hccl_context, global_state, Communicator::LOCAL),
        mpi_context_(mpi_context){};

  Status Execute(std::vector<TensorTableEntry>& entries,
                 const Response& response) override;

  bool Enabled(const ParameterManager& param_manager,
               const std::vector<TensorTableEntry>& entries,
               const Response& response) const override;

private:
  MPIContext* mpi_context_;
};

class HCCLHierarchicalBroadcast : public HCCLBroadcast {
public:
  HCCLHierarchicalBroadcast(HCCLContext* hccl_context, MPIContext* mpi_context,
                            HorovodGlobalState* global_state)
      : HCCLBroadcast(hccl_context, global_state, Communicator::LOCAL),
        mpi_context_(mpi_context){};

  Status Execute(std::vector<TensorTableEntry>& entries,
                 const Response& response) override;

  bool Enabled(const ParameterManager& param_manager,
               const std::vector<TensorTableEntry>& entries,
               const Response& response) const override;

private:
  MPIContext* mpi_context_;
};

#endif // HAVE_MPI

// std::pair order_index, executuion order
using OrderingKey = std::pair<int, int>;

struct OrderingKeyCompare {
  bool operator()(const OrderingKey& lhs, const OrderingKey& rhs) {
    if (lhs.second == rhs.second) {
      return lhs.first < rhs.first;
    }
    return lhs.second < rhs.second;
  }
};

struct QueueEntry {
  TensorTableEntry tensor_entry;
  OrderingKey key;
  bool ready;
  bool sent;
};

class OrderedOpContext;

class OrderingGroup {
public:
  OrderingGroup(size_t size, std::vector<int32_t> device_map)
      : group_size_(size), queue_items_sent_(0), device_map_(device_map) {}

  bool group_completed() { return (group_size_ == queue_items_sent_); }

  void AddEntry(TensorTableEntry&& entry);
  std::vector<TensorTableEntry> GetEntriesToSchedule();

  std::vector<int32_t>& device_map() { return device_map_; }

private:
  int ShouldWaitForMoreEntries(int requested_batch_size);

  std::map<int, int> order_index_to_list_index_;
  std::vector<QueueEntry> ordered_queue_;
  size_t group_size_;
  size_t queue_items_sent_;
  std::vector<bool> items_ready_;
  std::vector<bool> items_sent_;
  std::vector<int32_t> device_map_;
};

class OrderedOpContext {

public:
  OrderingGroup& GetOrderingGroup(const std::set<int>& ordering_indices,
                                  std::vector<int32_t>);
  void RemoveOrderingGroupIfCompleted(const std::set<int>& indices);

private:
  std::map<std::set<int>, OrderingGroup> ordering_groups_;
};

class HCCLSignaledAllreduce : public HCCLAllreduce {
public:
  HCCLSignaledAllreduce(HCCLContext* hccl_context,
                        HorovodGlobalState* global_state)
      : HCCLAllreduce(hccl_context, global_state, Communicator::GLOBAL){};

  Status Execute(std::vector<TensorTableEntry>& entries,
                 const Response& response) override;

  virtual bool Enabled(const ParameterManager& param_manager,
                       const std::vector<TensorTableEntry>& entries,
                       const Response& response) const override;

protected:
  virtual void ScheduleAllreduce(std::vector<TensorTableEntry>& entries,
                                 std::vector<int32_t>& device_map);

  void FinalizeEntries(std::vector<TensorTableEntry>& entries);

private:
  std::mutex execute_mutex_;
  OrderedOpContext ordered_op_context_;
};

class HCCLDummySignaledAllreduce : public HCCLSignaledAllreduce {
public:
  HCCLDummySignaledAllreduce(HCCLContext* hccl_context,
                             HorovodGlobalState* global_state)
      : HCCLSignaledAllreduce(hccl_context, global_state) {}

  virtual bool Enabled(const ParameterManager& param_manager,
                       const std::vector<TensorTableEntry>& entries,
                       const Response& response) const override;

protected:
  virtual void ScheduleAllreduce(std::vector<TensorTableEntry>& entries,
                                 std::vector<int32_t>& device_map) override;
};

} // namespace common
} // namespace horovod

#endif // HAVE_HCCL

#endif // HOROVOD_HCCL_OPERATIONS_H
