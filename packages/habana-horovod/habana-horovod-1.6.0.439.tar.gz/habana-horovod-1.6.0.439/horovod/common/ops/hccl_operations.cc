// Copyright 2016 The TensorFlow Authors. All Rights Reserved.
// Modifications copyright (C) 2019 Uber Technologies, Inc.
// Modifications copyright (C) 2020, NVIDIA CORPORATION. All rights reserved.
// Modifications copyright (C) 2021, Intel Corporation All rights reserved.
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

#include <absl/memory/memory.h>
#include <synapse_api.h>

#include "hccl_tracing.h"

#include "hccl_integration.h"
#include "hccl_operations.h"

namespace horovod {
namespace common {

hcclDataType_t GetHCCLDataType(const DataType data_type) {
  switch (data_type) {
  case HOROVOD_UINT8:
    return hcclUint8;
  case HOROVOD_INT8:
    return hcclInt8;
  case HOROVOD_INT32:
    return hcclInt32;
  case HOROVOD_INT64:
    return hcclInt64;
  case HOROVOD_FLOAT16:
    return hcclFloat16;
  case HOROVOD_FLOAT32:
    return hcclFloat32;
  case HOROVOD_FLOAT64:
    return hcclFloat64;
  case HOROVOD_BFLOAT16:
    return hcclBfloat16;
  default:
    throw std::logic_error("Type " + DataType_Name(data_type) +
                           " is not supported in HCCL mode.");
  }
}

HPUDeviceContext::HPUDeviceContext(int device_id) : device_id_(device_id) {
  LOG(TRACE) << "Entry " << __PRETTY_FUNCTION__;
  hcclResult_t hccl_status = hcclxOpenDevice(device_id);
  HCCL_OP_ASSERT(hcclSuccess == hccl_status);

  // The actual stream creation is postponed upon their first usage.
}

HPUDeviceContext::~HPUDeviceContext() {
  LOG(TRACE) << "Entry " << __PRETTY_FUNCTION__;
  release_collective_stream();
  release_copy_streams();
  hcclxCloseDevice(device_id_);
}

synStreamHandle HPUDeviceContext::collective_stream() {
  if (collective_stream_ == nullptr) {
    const hcclResult_t hccl_status =
        hcclxAcquireCollectiveStream(device_id(), &collective_stream_);
    if (hcclSuccess != hccl_status) {
      LOG(FATAL) << "Failed to acquire a collective stream.";
    }
    HCCL_OP_ASSERT(collective_stream_ != nullptr);
  }

  return collective_stream_;
}

synStreamHandle HPUDeviceContext::d2h_stream() {
  if (d2h_stream_ == nullptr) {
    const hcclResult_t hccl_status = hcclxAcquireCopyStream(
        device_id(), &d2h_stream_, hcclxMemcpyDeviceToHost);
    if (hcclSuccess != hccl_status) {
      LOG(FATAL) << "Failed to acquire a device-to-host copy stream.";
    }
    HCCL_OP_ASSERT(d2h_stream_ != nullptr);
  }

  return d2h_stream_;
}

synStreamHandle HPUDeviceContext::h2d_stream() {
  if (h2d_stream_ == nullptr) {
    const hcclResult_t hccl_status = hcclxAcquireCopyStream(
        device_id(), &h2d_stream_, hcclxMemcpyHostToDevice);
    if (hcclSuccess != hccl_status) {
      LOG(FATAL) << "Failed to acquire a host-to-device copy stream.";
    }
    HCCL_OP_ASSERT(h2d_stream_ != nullptr);
  }

  return h2d_stream_;
}

synStreamHandle HPUDeviceContext::d2d_stream() {
  if (d2d_stream_ == nullptr) {
    const hcclResult_t hccl_status = hcclxAcquireCopyStream(
        device_id(), &d2d_stream_, hcclxMemcpyDeviceToDevice);
    if (hcclSuccess != hccl_status) {
      LOG(FATAL) << "Failed to acquire a device-to-device copy stream.";
    }
    HCCL_OP_ASSERT(d2d_stream_ != nullptr);
  }

  return d2d_stream_;
}

void HPUDeviceContext::release_collective_stream() {
  if (collective_stream_ != nullptr) {
    hcclResult_t hccl_status = hcclxReleaseCollectiveStream(collective_stream_);
    HCCL_OP_ASSERT(hccl_status == hcclSuccess);
    collective_stream_ = nullptr;
  }
}

void HPUDeviceContext::release_copy_streams() {
  if (d2h_stream_ != nullptr) {
    hcclResult_t hccl_status = hcclxReleaseCopyStream(d2h_stream_);
    HCCL_OP_ASSERT(hccl_status == hcclSuccess);
    d2h_stream_ = nullptr;
  }
  if (h2d_stream_ != nullptr) {
    hcclResult_t hccl_status = hcclxReleaseCopyStream(h2d_stream_);
    HCCL_OP_ASSERT(hccl_status == hcclSuccess);
    h2d_stream_ = nullptr;
  }

  if (d2d_stream_ != nullptr) {
    hcclResult_t hccl_status = hcclxReleaseCopyStream(d2d_stream_);
    HCCL_OP_ASSERT(hccl_status == hcclSuccess);
    d2d_stream_ = nullptr;
  }
}

HPUDeviceContext* HCCLContext::OpenDevice(int device_id) {
  if (!IsDeviceOpen(device_id)) {
    opened_devices_[device_id] = absl::make_unique<HPUDeviceContext>(device_id);
  }
  return opened_devices_[device_id].get();
}

void HCCLContext::SetDevice(int device_id) { hcclxSetDevice(device_id); }

void HCCLContext::ShutDown() {
  LOG(TRACE) << __PRETTY_FUNCTION__ << " entry.";

  finalizer_thread_pool.reset();

  // Release collective stream
  // This has to be done prior to HCL_Destroy(). More info: SW-70726
  for (auto& device_iter : opened_devices_) {
    device_iter.second->release_collective_stream();
  }

  // Release communicators
  for (auto& comm_iter : hccl_comms) {
    hcclResult_t status = hcclCommDestroy(comm_iter.second);
    HCCL_OP_ASSERT(hcclSuccess == status);
  }
  hccl_comms.clear();

  // Release HPUDeviceContext
  for (auto& device_iter : opened_devices_) {
    if (hvd_global_ptr_) {
      hvd_global_ptr_->fusion_buffer.FreeDeviceBuffers(
          device_iter.second->device_id());
    }
  }
  opened_devices_.clear();
}

void HCCLOpContext::InitCommunicator(
    const std::vector<TensorTableEntry>& entries,
    const std::vector<int32_t>& hccl_device_map) {

  auto& first_entry = entries[0];
  if (nullptr == my_device_) {
    my_device_ = hccl_context_->OpenDevice(first_entry.device);
    HCCL_OP_ASSERT(nullptr != my_device_);
  }

  // Note: At this point all device ids are 0 (no multiple device support)
  //       Using device map here might cause issue when we move to multiple
  //       device per process.
  hcclComm_t& hccl_comm = hccl_context_->hccl_comms[hccl_device_map];

  if (nullptr == hccl_comm) {
    TRACE_SCOPE("InitCommunicator");
    LOG(TRACE) << "Initializing HCCL communicator.";
    auto& timeline = global_state_->timeline;
    timeline.ActivityStartAll(entries, INIT_HCCL);

    int hccl_rank, hccl_size;

    if (communicator_type_ == Communicator::GLOBAL) {
      hccl_rank = global_state_->global_controller->GetRank();
      hccl_size = global_state_->global_controller->GetSize();
    } else if (communicator_type_ == Communicator::LOCAL) {
      hccl_rank = global_state_->global_controller->GetLocalRank();
      hccl_size = global_state_->global_controller->GetLocalSize();
    } else {
      throw std::logic_error("Communicator type " +
                             std::to_string(communicator_type_) +
                             " is not supported in HCCL operations.");
    }
    hcclUniqueId hccl_id;

    if (hccl_rank == 0) {
      hcclResult_t result{hcclGetUniqueId(&hccl_id)};
      HCCL_OP_ASSERT(hcclSuccess == result);
    }
    // TODO: local communicators
    global_state_->global_controller->Bcast((void*)&hccl_id, sizeof(hccl_id), 0,
                                            communicator_type_);
    hcclComm_t new_comm;

    hcclResult_t result{
        hcclCommInitRank(&new_comm, hccl_size, hccl_id, hccl_rank)};
    HCCL_OP_ASSERT(hcclSuccess == result);
    hccl_comm = new_comm;

    global_state_->global_controller->Barrier(Communicator::GLOBAL);
    timeline.ActivityEndAll(entries);
  }

  hccl_comm_ = &hccl_comm;
  // Get reference from global ctx for given device
  // If null Bcast everything
}

void HCCLOpContext::InitDeviceQueue(
    const std::vector<TensorTableEntry>& entries,
    synStreamHandle initial_stream) {
  TRACE_SCOPE("InitDeviceQueue");
  LOG(TRACE) << "Entry " << __PRETTY_FUNCTION__;
  HCCL_OP_ASSERT(nullptr != my_device_);
  HCCL_OP_ASSERT(nullptr != current_stream_)

  hccl_context_->SetDevice(my_device_->device_id());

  std::vector<void*> input_addresses;
  input_addresses.resize(entries.size());

  for (unsigned ii = 0; ii < input_addresses.size(); ii++) {
    HCCL_OP_ASSERT(my_device_->device_id() == entries[ii].device);
    void* address{const_cast<void*>(entries[ii].tensor->data())};
    input_addresses[ii] = address;
  }

  hcclResult_t hccl_status = hcclxPrepareStream(
      initial_stream, input_addresses.data(), input_addresses.size());
  HCCL_OP_ASSERT(hcclSuccess == hccl_status);
}

// A helper structure to make use of C++ lambda in a C-style callback function.
struct EventSubmissionFinalizer {
  ///
  std::atomic<int> refcount;
  std::vector<TensorTableEntry> entries;
  ///
  std::function<void(const std::vector<TensorTableEntry>&)> on_done;

  void release() {
    if (0 == --refcount) {
      delete this;
    }
  }
};

// A function called by hcclxSubmitEvents() to notify about operation
// completion. Note that the call takes place from one of several Stream Event
// Manager's threads and is guarded by its internal mutex locks.
void EventSubmissionDoneCallback(hcclxCallbackCookie_t cookie) {
  auto* finalizer = reinterpret_cast<EventSubmissionFinalizer*>(cookie);
  HCCL_OP_ASSERT(finalizer != nullptr);
  if (finalizer->on_done) {
    // finalizer->on_done();
    finalizer->on_done(finalizer->entries);
  }
  finalizer->release();
}

Status
HCCLOpContext::FinalizeDeviceQueue(std::vector<TensorTableEntry>& entries,
                                   std::function<void()> on_finalize) {
  TRACE_SCOPE("FinalizeDeviceQueue");
  LOG(TRACE) << "Entry " << __PRETTY_FUNCTION__;

  Timeline& timeline = global_state_->timeline;

  const synStreamHandle stream_to_submit{current_stream_};
  if (stream_to_submit) {
    current_stream_ = nullptr;
    std::vector<void*> output_addresses;
    output_addresses.reserve(entries.size());

    for (auto& entry : entries) {
      HCCL_OP_ASSERT(my_device_->device_id() == entry.device);
      if (entry.output != nullptr) {
        void* address{const_cast<void*>(entry.output->data())};
        output_addresses.push_back(address);
      }
    }

    auto* finalizer = new EventSubmissionFinalizer{
        {2},
        std::move(entries),
        [on_finalize, &timeline](
            const std::vector<TensorTableEntry>& captured_entries) mutable {
          if (on_finalize) {
            on_finalize();
          };
          for (auto& e : captured_entries) {
            timeline.End(e.tensor_name, e.output);
          }
        }};

    hcclxSubmitEvents(stream_to_submit, output_addresses.data(),
                      output_addresses.size(), EventSubmissionDoneCallback,
                      finalizer);

    for (auto& e : finalizer->entries) {
      e.FinishWithCallback(Status::OK());
    }
    finalizer->release();

    return Status::InProgress();

    // Note that hccl_context_->finalizer_thread_pool.execute() is not called,
    // but finalization takes place on SEM event completion in its "done"
    // callback. Please refer to SW-48543 if you look for a reason for that.
  } else {
    // If there is no stream i means that everything was already synchronized.
    // No point of calling hcclxSubmitEvents or extending lifetime of tensors.
    if (on_finalize) {
      on_finalize();
    }
    return Status::OK();
  }
}

void HCCLOpContext::CopyDataToDevice(const void* src, void* dst, size_t size) {
  TRACE_SCOPE("CopyDataToDevice");
  LOG(TRACE) << "Entry " << __PRETTY_FUNCTION__;
  hcclResult_t hccl_status{hcclSuccess};
  void* device_destination = nullptr;
  hccl_status = hcclxLockDeviceAddress(dst, &device_destination);
  HCCL_OP_ASSERT(hcclSuccess == hccl_status);

  synStatus status = synMemCopyAsync(
      host_to_device_copy_stream(), reinterpret_cast<uint64_t>(src), size,
      reinterpret_cast<uint64_t>(device_destination), HOST_TO_DRAM);

  HCCL_OP_ASSERT(synSuccess == status);

  hccl_status = hcclxUnlockDeviceAddress(device_destination);
  HCCL_OP_ASSERT(hcclSuccess == hccl_status);
}

void HCCLOpContext::CopyDataToHost(void* src, void* dst, size_t size) {
  LOG(TRACE) << "Entry " << __PRETTY_FUNCTION__;
  hcclResult_t hccl_status{hcclSuccess};
  void* device_source = nullptr;
  hccl_status = hcclxLockDeviceAddress(src, &device_source);
  HCCL_OP_ASSERT(hcclSuccess == hccl_status);

  synStatus status = synMemCopyAsync(
      device_to_host_copy_stream(), reinterpret_cast<uint64_t>(device_source),
      size, reinterpret_cast<uint64_t>(dst), synDmaDir::DRAM_TO_HOST);
  HCCL_OP_ASSERT(synSuccess == status);

  hccl_status = hcclxUnlockDeviceAddress(device_source);
  HCCL_OP_ASSERT(hcclSuccess == hccl_status);
}

bool HCCLAllreduce::Enabled(const ParameterManager& param_manager,
                            const std::vector<TensorTableEntry>& entries,
                            const Response& response) const {
  bool is_enabled = (entries[0].device != CPU_DEVICE_ID) &&
                    !ShouldSkipHandshakeForAllreduce();
  LOG(TRACE) << "HCCLAllreduce is " << (is_enabled ? "enabled" : "disabled")
             << " for device: " << entries[0].device;
  return is_enabled;
}

Status HCCLAllreduce::Execute(std::vector<TensorTableEntry>& entries,
                              const Response& response) {
  TRACE_SCOPE("HCCLAllreduce::Execute");
  LOG(TRACE) << "Entry " << __PRETTY_FUNCTION__;

  op_context_.InitCommunicator(entries, response.devices());

  auto& timeline = global_state_->timeline;
  timeline.ActivityStartAll(entries, HCCL_ALLREDUCE);

  const bool fusion_buffer_in_use{entries.size() > 1};
  auto& first_entry = entries[0];

  const void* fused_input_data;
  void* buffer_data;
  size_t buffer_len;

  if (fusion_buffer_in_use) {
    op_context_.InitDeviceQueue(entries,
                                op_context_.within_device_copy_stream());
    MemcpyInFusionBuffer(entries, fused_input_data, buffer_data, buffer_len);
  } else {
    op_context_.InitDeviceQueue(entries, op_context_.collective_stream());
    fused_input_data = const_cast<void*>(first_entry.tensor->data());
    buffer_data = (void*)first_entry.output->data();
    buffer_len = (size_t)first_entry.output->size();
  }

  int64_t num_elements = 0;
  for (auto& e : entries) {
    num_elements += e.tensor->shape().num_elements();
  }

  void* input_address;
  void* output_address;
  hcclResult_t hccl_result{hcclSuccess};

  hccl_result = hcclxLockDeviceAddress(const_cast<void*>(fused_input_data),
                                       &input_address);
  HCCL_OP_ASSERT(hcclSuccess == hccl_result);

  hccl_result = hcclxLockDeviceAddress(buffer_data, &output_address);
  HCCL_OP_ASSERT(hcclSuccess == hccl_result);

  if (ShouldPutBarrierBeforeAllReduce()) {
    // hcclBarrier does not work.
    //
    // hccl_result =
    //     hcclBarrier(*op_context_.hccl_comm_,
    //     op_context_.collective_stream());
    // HCCL_OP_ASSERT(hcclSuccess == hccl_result);
    hccl_result =
        hcclAllReduce(input_address, output_address, (size_t)num_elements,
                      GetHCCLDataType(first_entry.tensor->dtype()), hcclSum,
                      *op_context_.hccl_comm_, op_context_.collective_stream());

    op_context_.SynchronizeCurrentStream();
    synStreamSynchronize(op_context_.collective_stream());
  }

  int slice_size{HcclAllreduceSliceSize()};

  if (0 == slice_size) {
    hccl_result =
        hcclAllReduce(input_address, output_address, (size_t)num_elements,
                      GetHCCLDataType(first_entry.tensor->dtype()), hcclSum,
                      *op_context_.hccl_comm_, op_context_.collective_stream());
    SYNC_AFTER_HCCL_IF_NEED(op_context_);
    HCCL_OP_ASSERT(hcclSuccess == hccl_result);
  } else {
    static bool log_once{true};
    if (log_once) {
      LOG(WARNING) << "Using sliced allreduce implementation. Slice size:"
                   << slice_size;
      log_once = false;
    }

    HCCL_OP_ASSERT(slice_size > 0);
    size_t single_elem_size{DataType_Size(first_entry.tensor->dtype())};

    size_t data_offset = 0;
    size_t slice_elem_cnt = static_cast<size_t>(slice_size) / single_elem_size;
    HCCL_OP_ASSERT(slice_size % single_elem_size == 0);

    while (num_elements > 0) {
      size_t num_elements_in_current_chunk =
          ((size_t)num_elements > slice_elem_cnt) ? slice_elem_cnt
                                                  : (size_t)num_elements;
      LOG(TRACE) << "Reducing partially " << num_elements_in_current_chunk
                 << " elements from " << num_elements;
      hccl_result = hcclAllReduce(
          reinterpret_cast<const uint8_t*>(input_address) + data_offset,
          reinterpret_cast<uint8_t*>(output_address) + data_offset,
          num_elements_in_current_chunk,
          GetHCCLDataType(first_entry.tensor->dtype()), hcclSum,
          *op_context_.hccl_comm_, op_context_.collective_stream());
      SYNC_AFTER_HCCL_IF_NEED(op_context_);
      HCCL_OP_ASSERT(hcclSuccess == hccl_result);
      data_offset += static_cast<size_t>(slice_size);
      num_elements -= num_elements_in_current_chunk;
    }
    HCCL_OP_ASSERT(0 == num_elements);
  }

  hccl_result = hcclxUnlockDeviceAddress(input_address);
  HCCL_OP_ASSERT(hcclSuccess == hccl_result);

  hccl_result = hcclxUnlockDeviceAddress(output_address);
  HCCL_OP_ASSERT(hcclSuccess == hccl_result);

  if (fusion_buffer_in_use) {
    MemcpyOutFusionBuffer(buffer_data, entries);
  }

  return op_context_.FinalizeDeviceQueue(entries);
}

void HCCLAllreduce::MemcpyInFusionBuffer(
    const std::vector<TensorTableEntry>& entries, const void*& fused_input_data,
    void*& buffer_data, size_t& buffer_len) {
  TRACE_SCOPE("MemcpyInFusionBuffer");
  LOG(TRACE) << "Entry " << __PRETTY_FUNCTION__;

  hcclResult_t hccl_result{hcclSuccess};

  // Access the fusion buffer.
  auto& first_entry = entries[0];
  auto buffer = global_state_->fusion_buffer.GetBuffer(
      first_entry.device, first_entry.context->framework(),
      global_state_->current_nccl_stream);
  buffer_data = const_cast<void*>(buffer->AccessData(first_entry.context));

  std::vector<uint64_t> sources;
  std::vector<uint64_t> destinations;
  std::vector<uint64_t> sizes;
  sources.resize(entries.size());
  destinations.resize(entries.size());
  sizes.resize(entries.size());

  int64_t offset = 0;

  for (unsigned idx = 0; idx < entries.size(); idx++) {
    void* buffer_data_at_offset = (uint8_t*)buffer_data + offset;

    void* src_addr;
    void* dst_addr;

    hccl_result =
        hcclxLockDeviceAddress((void*)entries[idx].tensor->data(), &src_addr);
    HCCL_OP_ASSERT(hcclSuccess == hccl_result);
    hccl_result =
        hcclxLockDeviceAddress((void*)buffer_data_at_offset, &dst_addr);
    HCCL_OP_ASSERT(hcclSuccess == hccl_result);

    sources[idx] = (uint64_t)src_addr;
    sizes[idx] = (uint64_t)entries[idx].tensor->size();
    destinations[idx] = (uint64_t)dst_addr;
    offset += entries[idx].tensor->size();
  }

  synStatus synapse_status{synMemCopyAsyncMultiple(
      op_context_.within_device_copy_stream(), sources.data(), sizes.data(),
      destinations.data(), DRAM_TO_DRAM, entries.size())};
  HCCL_OP_ASSERT(synSuccess == synapse_status);

  for (unsigned idx = 0; idx < entries.size(); idx++) {
    hccl_result = hcclxUnlockDeviceAddress((void*)sources[idx]);
    HCCL_OP_ASSERT(hcclSuccess == hccl_result);
    hccl_result = hcclxUnlockDeviceAddress((void*)destinations[idx]);
    HCCL_OP_ASSERT(hcclSuccess == hccl_result);
  }

  buffer_len = (size_t)offset;

  fused_input_data = buffer_data;
}

void HCCLAllreduce::MemcpyOutFusionBuffer(
    const void* buffer_data, std::vector<TensorTableEntry>& entries) {
  TRACE_SCOPE("MemcpyInFusionBuffer");
  LOG(TRACE) << "Entry " << __PRETTY_FUNCTION__;
  hcclResult_t hccl_result{hcclSuccess};

  std::vector<uint64_t> sources;
  std::vector<uint64_t> destinations;
  std::vector<uint64_t> sizes;
  sources.resize(entries.size());
  destinations.resize(entries.size());
  sizes.resize(entries.size());

  int64_t offset = 0;

  for (unsigned idx = 0; idx < entries.size(); idx++) {
    void* buffer_data_at_offset = (uint8_t*)buffer_data + offset;

    void* src_addr;
    void* dst_addr;

    hccl_result =
        hcclxLockDeviceAddress((void*)buffer_data_at_offset, &src_addr);
    HCCL_OP_ASSERT(hcclSuccess == hccl_result);
    hccl_result =
        hcclxLockDeviceAddress((void*)entries[idx].output->data(), &dst_addr);
    HCCL_OP_ASSERT(hcclSuccess == hccl_result);

    sources[idx] = (uint64_t)src_addr;
    sizes[idx] = (uint64_t)entries[idx].tensor->size();
    destinations[idx] = (uint64_t)dst_addr;
    offset += entries[idx].output->size();
  }

  synStatus synapse_status{synMemCopyAsyncMultiple(
      op_context_.within_device_copy_stream(), sources.data(), sizes.data(),
      destinations.data(), DRAM_TO_DRAM, entries.size())};
  HCCL_OP_ASSERT(synSuccess == synapse_status);

  for (unsigned idx = 0; idx < entries.size(); idx++) {
    hccl_result = hcclxUnlockDeviceAddress((void*)sources[idx]);
    HCCL_OP_ASSERT(hcclSuccess == hccl_result);
    hccl_result = hcclxUnlockDeviceAddress((void*)destinations[idx]);
    HCCL_OP_ASSERT(hcclSuccess == hccl_result);
  }
}

bool HCCLAllgather::Enabled(const ParameterManager& param_manager,
                            const std::vector<TensorTableEntry>& entries,
                            const Response& response) const {
  bool is_enabled = (entries[0].device != CPU_DEVICE_ID);
  LOG(TRACE) << "HCCLAllgather is " << (is_enabled ? "enabled" : "disabled")
             << " for device: " << entries[0].device;
  return is_enabled;
}

HCCLAllgather::FusionData::FusionData(int comm_size, size_t tensor_count,
                                      size_t element_size)
    : tensor_count_(tensor_count), element_size_(element_size) {
  HCCL_OP_ASSERT(element_size % 2 == 0);
  entry_component_sizes_ = new int64_t*[tensor_count_];
  entry_component_offsets_ = new int64_t*[tensor_count_];

  for (size_t entry_idx = 0; entry_idx < tensor_count_; ++entry_idx) {
    entry_component_sizes_[entry_idx] = new int64_t[comm_size]();
    entry_component_offsets_[entry_idx] = new int64_t[comm_size]();
  }

  recieve_data_counts_ = new int[comm_size]();
  displacements_ = new int[comm_size]();
}

HCCLAllgather::FusionData::~FusionData() {
  for (size_t entry_idx = 0; entry_idx < tensor_count_; ++entry_idx) {
    delete[] entry_component_sizes_[entry_idx];
    delete[] entry_component_offsets_[entry_idx];
  }

  delete[] entry_component_sizes_;
  delete[] entry_component_offsets_;
  delete[] recieve_data_counts_;
  delete[] displacements_;
}

Status HCCLAllgather::Execute(std::vector<TensorTableEntry>& entries,
                              const Response& response) {
  LOG(TRACE) << "Entry " << __PRETTY_FUNCTION__;

  op_context_.InitCommunicator(entries, response.devices());

  auto& timeline = global_state_->timeline;
  timeline.ActivityStartAll(entries, ALLOCATE_OUTPUT);

  int comm_size{global_state_->global_controller->GetSize()};
  int global_rank{global_state_->global_controller->GetRank()};

  TensorTableEntry& first_entry = entries[0];
  size_t single_elem_size = DataType_Size(first_entry.tensor->dtype());

  FusionData fusion_data{comm_size, entries.size(), single_elem_size};

  Status status =
      AllocateOutput(entries, response, fusion_data.entry_component_sizes(),
                     fusion_data.recieve_data_counts());
  timeline.ActivityEndAll(entries);
  if (!status.ok()) {
    return status;
  }

  SetDisplacements(fusion_data.recieve_data_counts(),
                   fusion_data.displacements(), comm_size);
  SetEntryComponentOffsets(entries, fusion_data.entry_component_sizes(),
                           fusion_data.recieve_data_counts(),
                           fusion_data.entry_component_offsets());

  const void* fused_input_data;
  void* buffer_data;

  if (entries.size() > 1) {
    op_context_.InitDeviceQueue(entries,
                                op_context_.within_device_copy_stream());
    LOG(DEBUG) << "Perfroming HCCLAllgather for " << entries.size()
               << " fused tensors";
    MemcpyInFusionBuffer(entries, fused_input_data, buffer_data,
                         fusion_data.GetInputOffset(global_rank));
  } else {
    op_context_.InitDeviceQueue(entries, op_context_.collective_stream());
    LOG(DEBUG) << "Perfroming HCCLAllgather for single tensor ["
               << first_entry.tensor_name << "]";
    fused_input_data = first_entry.tensor->data();
    buffer_data = (void*)first_entry.output->data();
  }

  bool same_shape{SameShape(entries, response, comm_size)};
  hcclResult_t hccl_result{hcclSuccess};

  if (same_shape) {
    timeline.ActivityStartAll(entries, HCCL_ALLGATHER);
    void* send_buffer;
    void* recv_buffer;
    LOG(INFO) << first_entry.tensor_name;
    hccl_result = hcclxLockDeviceAddress(const_cast<void*>(fused_input_data),
                                         &send_buffer);
    HCCL_OP_ASSERT(hcclSuccess == hccl_result);

    bool lock_output{fused_input_data != buffer_data};

    if (lock_output) {
      hccl_result =
          hcclxLockDeviceAddress(const_cast<void*>(buffer_data), &recv_buffer);
      HCCL_OP_ASSERT(hcclSuccess == hccl_result);
    } else {
      recv_buffer = send_buffer;
    }

    hcclResult_t hccl_result = hcclAllGather(
        send_buffer, recv_buffer, fusion_data.GetRecvCount(0), hcclBfloat16,
        *op_context_.hccl_comm_, op_context_.collective_stream());
    HCCL_OP_ASSERT(hcclSuccess == hccl_result);
    SYNC_AFTER_HCCL_IF_NEED(op_context_);

    hccl_result = hcclxUnlockDeviceAddress(send_buffer);
    HCCL_OP_ASSERT(hcclSuccess == hccl_result);
    if (lock_output) {
      hccl_result = hcclxUnlockDeviceAddress(recv_buffer);
      HCCL_OP_ASSERT(hcclSuccess == hccl_result);
    }
  } else {
    LOG(WARNING) << "HCCLAllgather for tensors with different shapes "
                    "(between ranks) is "
                    "inefficient.";
    timeline.ActivityStartAll(entries, HCCL_BROADCAST);
    for (int rank_idx = 0; rank_idx < comm_size; rank_idx++) {
      void* send_buff;
      void* recv_buff;
      hccl_result = hcclxLockDeviceAddress(const_cast<void*>(fused_input_data),
                                           &send_buff);
      HCCL_OP_ASSERT(hcclSuccess == hccl_result);

      void* new_buffer_data{(uint8_t*)buffer_data +
                            fusion_data.GetInputOffset(rank_idx)};
      bool lock_output{fused_input_data != new_buffer_data};
      if (lock_output) {
        hccl_result = hcclxLockDeviceAddress(const_cast<void*>(new_buffer_data),
                                             &recv_buff);
        HCCL_OP_ASSERT(hcclSuccess == hccl_result);
      } else {
        recv_buff = send_buff;
      }

      LOG(TRACE) << "Calling hcclBroadcast";
      hcclResult_t hccl_result = hcclBroadcast(
          send_buff, recv_buff, fusion_data.GetRecvCount(rank_idx),
          hcclBfloat16, rank_idx, *op_context_.hccl_comm_,
          op_context_.collective_stream());
      HCCL_OP_ASSERT(hcclSuccess == hccl_result);
      SYNC_AFTER_HCCL_IF_NEED(op_context_);

      hccl_result = hcclxUnlockDeviceAddress(send_buff);
      HCCL_OP_ASSERT(hcclSuccess == hccl_result);
      if (lock_output) {
        hccl_result = hcclxUnlockDeviceAddress(recv_buff);
        HCCL_OP_ASSERT(hcclSuccess == hccl_result);
      }
    }
  }

  if (entries.size() > 1) {
    MemcpyOutFusionBuffer(buffer_data, entries, fusion_data);
  }
  return op_context_.FinalizeDeviceQueue(entries);
}

void HCCLAllgather::MemcpyInFusionBuffer(
    const std::vector<TensorTableEntry>& entries, const void*& fused_input_data,
    void*& buffer_data, int64_t initial_offset) {
  LOG(TRACE) << "Entry " << __PRETTY_FUNCTION__;

  hcclResult_t hccl_result{hcclSuccess};

  // Access the fusion buffer.
  auto& first_entry = entries[0];
  auto buffer = global_state_->fusion_buffer.GetBuffer(
      first_entry.device, first_entry.context->framework(),
      global_state_->current_nccl_stream);
  buffer_data = const_cast<void*>(buffer->AccessData(first_entry.context));

  std::vector<uint64_t> sources;
  std::vector<uint64_t> destinations;
  std::vector<uint64_t> sizes;
  sources.resize(entries.size());
  destinations.resize(entries.size());
  sizes.resize(entries.size());

  int64_t offset = initial_offset;
  fused_input_data = reinterpret_cast<uint8_t*>(buffer_data) + initial_offset;

  for (unsigned idx = 0; idx < entries.size(); idx++) {
    void* buffer_data_at_offset = (uint8_t*)buffer_data + offset;

    void* src_addr;
    void* dst_addr;

    hccl_result =
        hcclxLockDeviceAddress((void*)entries[idx].tensor->data(), &src_addr);
    HCCL_OP_ASSERT(hcclSuccess == hccl_result);
    hccl_result =
        hcclxLockDeviceAddress((void*)buffer_data_at_offset, &dst_addr);
    HCCL_OP_ASSERT(hcclSuccess == hccl_result);

    sources[idx] = (uint64_t)src_addr;
    sizes[idx] = (uint64_t)entries[idx].tensor->size();
    destinations[idx] = (uint64_t)dst_addr;
    offset += entries[idx].tensor->size();
  }

  synStatus synapse_status{synMemCopyAsyncMultiple(
      op_context_.within_device_copy_stream(), sources.data(), sizes.data(),
      destinations.data(), DRAM_TO_DRAM, entries.size())};
  HCCL_OP_ASSERT(synSuccess == synapse_status);

  for (unsigned idx = 0; idx < entries.size(); idx++) {
    hccl_result = hcclxUnlockDeviceAddress((void*)sources[idx]);
    HCCL_OP_ASSERT(hcclSuccess == hccl_result);
    hccl_result = hcclxUnlockDeviceAddress((void*)destinations[idx]);
    HCCL_OP_ASSERT(hcclSuccess == hccl_result);
  }
}

void HCCLAllgather::MemcpyOutFusionBuffer(
    void*& buffer_data, const std::vector<TensorTableEntry>& entries,
    HCCLAllgather::FusionData& fusion_data) {
  LOG(TRACE) << "Entry " << __PRETTY_FUNCTION__;

  hcclResult_t hccl_result{hcclSuccess};

  // Access the fusion buffer.
  auto& first_entry = entries[0];
  auto buffer = global_state_->fusion_buffer.GetBuffer(
      first_entry.device, first_entry.context->framework(),
      global_state_->current_nccl_stream);
  buffer_data = const_cast<void*>(buffer->AccessData(first_entry.context));

  std::vector<uint64_t> sources;
  std::vector<uint64_t> destinations;
  std::vector<uint64_t> sizes;
  int global_size = global_state_->global_controller->GetSize();
  sources.reserve(entries.size() * global_size);
  destinations.reserve(entries.size() * global_size);
  sizes.reserve(entries.size() * global_size);

  for (size_t entry_idx = 0; entry_idx < entries.size(); entry_idx++) {
    auto& current_entry = entries[entry_idx];
    int64_t copy_offset = 0;
    for (int rank = 0; rank < global_size; rank++) {
      int64_t entry_offset =
          fusion_data.entry_component_offsets()[entry_idx][rank] *
          fusion_data.element_size();
      int64_t entry_size =
          fusion_data.entry_component_sizes()[entry_idx][rank] *
          fusion_data.element_size();
      void* const buffer_data_at_offset{(uint8_t*)buffer_data + entry_offset};
      void* const output_data_at_offset{(uint8_t*)current_entry.output->data() +
                                        copy_offset};

      void* src_addr;
      void* dst_addr;

      hccl_result = hcclxLockDeviceAddress(buffer_data_at_offset, &src_addr);
      HCCL_OP_ASSERT(hcclSuccess == hccl_result);
      hccl_result = hcclxLockDeviceAddress(output_data_at_offset, &dst_addr);
      HCCL_OP_ASSERT(hcclSuccess == hccl_result);

      sources.push_back((uint64_t)src_addr);
      sizes.push_back((uint64_t)entry_size);
      destinations.push_back((uint64_t)dst_addr);
      copy_offset += entry_size;
    }
  }

  synStatus synapse_status{synMemCopyAsyncMultiple(
      op_context_.within_device_copy_stream(), sources.data(), sizes.data(),
      destinations.data(), DRAM_TO_DRAM, sizes.size())};
  HCCL_OP_ASSERT(synSuccess == synapse_status);

  for (unsigned idx = 0; idx < sizes.size(); idx++) {
    hccl_result = hcclxUnlockDeviceAddress((void*)sources[idx]);
    HCCL_OP_ASSERT(hcclSuccess == hccl_result);
    hccl_result = hcclxUnlockDeviceAddress((void*)destinations[idx]);
    HCCL_OP_ASSERT(hcclSuccess == hccl_result);
  }
}

bool HCCLAllgather::SameShape(std::vector<TensorTableEntry>& entries,
                              const Response& response, int global_size) {
  bool same_shape = true;
  const auto& tensor_sizes = response.tensor_sizes();
  for (size_t ec = 0; ec < entries.size(); ++ec) {
    for (int rc = 1; rc < global_size; ++rc) {
      if (tensor_sizes[ec * global_size + rc] !=
          tensor_sizes[ec * global_size]) {
        same_shape = false;
        break;
      }
    }
    if (same_shape == false) {
      break;
    }
  }
  return same_shape;
}

bool HCCLAlltoall::Enabled(const ParameterManager& param_manager,
                           const std::vector<TensorTableEntry>& entries,
                           const Response& response) const {
  bool is_enabled = (entries[0].device != CPU_DEVICE_ID);
  LOG(TRACE) << "HCCLAlltoall is " << (is_enabled ? "enabled" : "disabled")
             << " for device: " << entries[0].device;
  return is_enabled;
}

Status HCCLAlltoall::Execute(std::vector<TensorTableEntry>& entries,
                             const Response& response) {
  LOG(TRACE) << "Entry " << __PRETTY_FUNCTION__;

  HCCL_OP_ASSERT(entries.size() == 1);

  TensorTableEntry& entry = entries[0];

  op_context_.InitCommunicator(entries, response.devices());
  op_context_.InitDeviceQueue(entries, op_context_.within_device_copy_stream());

  std::vector<int32_t> sdispls, rdispls;
  std::vector<int32_t> sendcounts, recvcounts;
  Status status =
      PrepareOutputAndParams(entry, sdispls, rdispls, sendcounts, recvcounts);
  if (!status.ok()) {
    return status;
  }

  auto comm_size = global_state_->global_controller->GetSize();
  auto my_rank = global_state_->global_controller->GetRank();

  hcclResult_t hccl_result{hcclSuccess};

  void* input_address;
  void* output_address;
  size_t elem_size = DataType_Size(entry.tensor->dtype());

  hccl_result = hcclxLockDeviceAddress(const_cast<void*>(entry.tensor->data()),
                                       &input_address);
  HCCL_OP_ASSERT(hcclSuccess == hccl_result);

  hccl_result = hcclxLockDeviceAddress(const_cast<void*>(entry.output->data()),
                                       &output_address);
  HCCL_OP_ASSERT(hcclSuccess == hccl_result);

  hccl_result = hcclGroupStart();
  HCCL_OP_ASSERT(hcclSuccess == hccl_result);

  for (int rank_idx = 0; rank_idx < comm_size; rank_idx++) {
    if (rank_idx == my_rank) {
      // TODO: HCCL does not support send/recv withing the same rank
      continue;
    }
    if (recvcounts[rank_idx] > 0) {
      void* recv_addr =
          (uint8_t*)output_address + rdispls[rank_idx] * elem_size;
      size_t recv_size = recvcounts[rank_idx] * elem_size;
      LOG(ERROR) << "Recv from rank " << rank_idx
                 << " recv_address: " << std::hex << recv_addr << " ("
                 << std::dec << recv_size << " bytes) buff start: " << std::hex
                 << output_address;
      hccl_result =
          hcclRecv(recv_addr, recv_size, hcclChar, rank_idx,
                   *op_context_.hccl_comm_, op_context_.collective_stream());
      HCCL_OP_ASSERT(hcclSuccess == hccl_result);
    }
    if (sendcounts[rank_idx] > 0) {
      void* send_addr = (uint8_t*)input_address + sdispls[rank_idx] * elem_size;
      size_t send_size = sendcounts[rank_idx] * elem_size;
      LOG(ERROR) << "Send to rank " << rank_idx << " send_addr: " << std::hex
                 << send_addr << " (" << std::dec << send_size
                 << " bytes) buff start: " << std::hex << input_address;
      hccl_result =
          hcclSend(send_addr, send_size, hcclChar, rank_idx,
                   *op_context_.hccl_comm_, op_context_.collective_stream());
      HCCL_OP_ASSERT(hcclSuccess == hccl_result);
    }
  }

  hccl_result = hcclGroupEnd();
  HCCL_OP_ASSERT(hcclSuccess == hccl_result);
  op_context_.SynchronizeCurrentStream();

  // Send/recv from yourself
  uint64_t src_address{(uint64_t)input_address + sdispls[my_rank] * elem_size};
  uint64_t dst_address{(uint64_t)output_address + rdispls[my_rank] * elem_size};
  size_t data_size{recvcounts[my_rank] * elem_size};
  HCCL_OP_ASSERT(recvcounts[my_rank] == sendcounts[my_rank]);

  LOG(ERROR) << "Issuing copy from " << std::hex << src_address << " to "
             << dst_address << " (" << std::dec << data_size << " bytes)";
  synStatus synapse_status{
      synMemCopyAsync(op_context_.within_device_copy_stream(), src_address,
                      data_size, dst_address, DRAM_TO_DRAM)};
  HCCL_OP_ASSERT(synSuccess == synapse_status);
  op_context_.SynchronizeCurrentStream();

  hccl_result = hcclxUnlockDeviceAddress(input_address);
  HCCL_OP_ASSERT(hcclSuccess == hccl_result);
  hccl_result = hcclxUnlockDeviceAddress(output_address);
  HCCL_OP_ASSERT(hcclSuccess == hccl_result);

  return op_context_.FinalizeDeviceQueue(entries);
}

bool HCCLReduceScatter::Enabled(const ParameterManager& param_manager,
                                const std::vector<TensorTableEntry>& entries,
                                const Response& response) const {
  bool is_enabled = (entries[0].device != CPU_DEVICE_ID);
  LOG(TRACE) << "HCCLReduceScatter is " << (is_enabled ? "enabled" : "disabled")
             << " for device: " << entries[0].device;
  return is_enabled;
}

Status HCCLReduceScatter::Execute(std::vector<TensorTableEntry>& entries,
                                  const Response& response) {
  LOG(TRACE) << "Entry " << __PRETTY_FUNCTION__;

  HCCL_OP_ASSERT(entries.size() == 1);
  int global_size = global_state_->global_controller->GetSize();
  int my_rank = global_state_->global_controller->GetRank();

  TensorTableEntry& entry = entries[0];

  op_context_.InitCommunicator(entries, response.devices());
  op_context_.InitDeviceQueue(entries, op_context_.collective_stream());

  int64_t num_elements, num_elements_remainder;

  auto& timeline = global_state_->timeline;
  timeline.ActivityStartAll(entries, ALLOCATE_OUTPUT);
  Status status =
      PrepareOutputAndParams(entry, num_elements, num_elements_remainder);
  timeline.ActivityEndAll(entries);
  if (!status.ok()) {
    return status;
  }

  timeline.ActivityStartAll(entries, HCCL_REDUCE_SCATTER);

  void* input_data = (void*)entry.tensor->data();
  void* output_data = (void*)entry.output->data();

  HCCL_OP_ASSERT(output_data != nullptr);
  HCCL_OP_ASSERT(entry.output->shape().num_elements() >= num_elements);

  void* input_address;
  void* output_address;
  hcclResult_t hccl_result{hcclSuccess};

  hccl_result = hcclxLockDeviceAddress(input_data, &input_address);
  HCCL_OP_ASSERT(hcclSuccess == hccl_result);

  hccl_result = hcclxLockDeviceAddress(output_data, &output_address);
  HCCL_OP_ASSERT(hcclSuccess == hccl_result);

  hccl_result = hcclReduceScatter(input_address, output_address, num_elements,
                                  GetHCCLDataType(entry.tensor->dtype()),
                                  hcclSum, *op_context_.hccl_comm_,
                                  op_context_.collective_stream());
  HCCL_OP_ASSERT(hcclSuccess == hccl_result);
  SYNC_AFTER_HCCL_IF_NEED(op_context_);

  hccl_result = hcclxUnlockDeviceAddress(input_address);
  HCCL_OP_ASSERT(hcclSuccess == hccl_result);
  hccl_result = hcclxUnlockDeviceAddress(output_address);
  HCCL_OP_ASSERT(hcclSuccess == hccl_result);

  if (num_elements_remainder > 0) {
    int root_rank = global_size - 1;

    size_t element_size = DataType_Size(entry.tensor->dtype());

    size_t last_chunk_input_data_offset(num_elements * global_size *
                                        element_size);
    hccl_result = hcclxLockDeviceAddress(
        reinterpret_cast<uint8_t*>(input_data) + last_chunk_input_data_offset,
        &input_address);
    HCCL_OP_ASSERT(hcclSuccess == hccl_result);

    if (root_rank == my_rank) {
      size_t last_chunk_output_data_offset(num_elements * element_size);
      hccl_result =
          hcclxLockDeviceAddress(reinterpret_cast<uint8_t*>(output_data) +
                                     last_chunk_output_data_offset,
                                 &output_address);
      HCCL_OP_ASSERT(hcclSuccess == hccl_result);
    } else {
      // TODO: We should be able to pass nullptr here but for some reasons
      // hcclReduce is accessing output buffer even on non root ranks
      // see [SW-67333]
      output_address = input_address;
    }

    hccl_result =
        hcclReduce(input_address, output_address, num_elements_remainder,
                   GetHCCLDataType(entry.tensor->dtype()), hcclSum, root_rank,
                   *op_context_.hccl_comm_, op_context_.collective_stream());

    HCCL_OP_ASSERT(hcclSuccess == hccl_result);
    SYNC_AFTER_HCCL_IF_NEED(op_context_);

    if (root_rank == my_rank) {
      hccl_result = hcclxUnlockDeviceAddress(output_address);
      HCCL_OP_ASSERT(hcclSuccess == hccl_result);
    }

    hccl_result = hcclxUnlockDeviceAddress(input_address);
    HCCL_OP_ASSERT(hcclSuccess == hccl_result);
  }

  return op_context_.FinalizeDeviceQueue(entries);
}

bool HCCLBroadcast::Enabled(const ParameterManager& param_manager,
                            const std::vector<TensorTableEntry>& entries,
                            const Response& response) const {
  bool is_enabled = (entries[0].device != CPU_DEVICE_ID);
  LOG(TRACE) << "HCCLBroadcast is " << (is_enabled ? "enabled" : "disabled")
             << " for device: " << entries[0].device;

  return is_enabled;
}

Status HCCLBroadcast::Execute(std::vector<TensorTableEntry>& entries,
                              const Response& response) {
  LOG(TRACE) << "Entry " << __PRETTY_FUNCTION__;

  op_context_.InitCommunicator(entries, response.devices());

  auto& timeline = global_state_->timeline;
  timeline.ActivityStartAll(entries, HCCL_BROADCAST);

  op_context_.InitDeviceQueue(entries, op_context_.collective_stream());
  hcclResult_t hccl_result{hcclSuccess};
  for (auto& entry : entries) {
    auto mpi_root{entry.root_rank};
    auto mpi_rank{global_state_->global_controller->GetRank()};

    const void* addr{(mpi_root == mpi_rank) ? entry.tensor->data()
                                            : entry.output->data()};
    void* device_address;

    hccl_result =
        hcclxLockDeviceAddress(const_cast<void*>(addr), &device_address);
    HCCL_OP_ASSERT(hcclSuccess == hccl_result);

    int root_rank{entry.root_rank};
    auto count{static_cast<size_t>(entry.tensor->shape().num_elements())};
    hcclDataType_t data_type = GetHCCLDataType(entry.tensor->dtype());

    hcclResult_t hccl_result = hcclBroadcast(
        device_address, device_address, count, data_type, root_rank,
        *op_context_.hccl_comm_, op_context_.collective_stream());
    HCCL_OP_ASSERT(hcclSuccess == hccl_result);

    SYNC_AFTER_HCCL_IF_NEED(op_context_);

    hccl_result = hcclxUnlockDeviceAddress(device_address);
    HCCL_OP_ASSERT(hcclSuccess == hccl_result);
  }
  return op_context_.FinalizeDeviceQueue(entries);
}

} // namespace common

} // namespace horovod
