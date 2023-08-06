#include <absl/memory/memory.h>
#include <synapse_api.h>

#include "hccl_integration.h"
#include "hccl_operations.h"

namespace horovod {
namespace common {

#if HAVE_MPI
// TODO: [SW-45079] This function performs a hiearchical allreduce using first
// hcclAllreduce, then MPI_Allreduce. It can be optimized to take advantage of
// hcclReduceScatter and hcclAllgather, so MPI exchanges less data through the
// host NIC.
Status
HCCLHierarchicalAllreduce::Execute(std::vector<TensorTableEntry>& entries,
                                   const Response& response) {
  LOG(TRACE) << "Entry " << __PRETTY_FUNCTION__;

  op_context_.InitCommunicator(entries, response.devices());

  auto& timeline = global_state_->timeline;
  timeline.ActivityStartAll(entries, HCCL_ALLREDUCE);

  synStatus syn_status{};
  hcclResult_t hccl_result{};

  auto& first_entry = entries[0];

  const bool fusion_buffer_in_use{entries.size() > 1};

  // Suporrt will be added later
  HCCL_OP_ASSERT(global_state_->global_controller->IsHomogeneous());

  const auto device_id = first_entry.device;

  const void* fused_input_data{};
  void* buffer_data{};
  size_t buffer_len{};

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

  int64_t num_elements =
      buffer_len / DataType_Size(first_entry.tensor->dtype());

  // * * * REDUCTION PHASE * * *
  // Do allreduce.
  int element_size = mpi_context_->GetMPITypeSize(first_entry.tensor->dtype());
  int local_size = global_state_->global_controller->GetLocalSize();
  int local_rank = global_state_->global_controller->GetLocalRank();

  if (fusion_buffer_in_use) {
    // Making sure the number of elements is divisible by
    // FUSION_BUFFER_ATOMIC_UNIT for improved performance
    int div = local_size * FUSION_BUFFER_ATOMIC_UNIT;
    num_elements = ((num_elements + div - 1) / div) * div;
    buffer_len = num_elements * element_size;
  }

  int64_t num_elements_per_rank = num_elements / local_size;

  size_t buffer_len_per_rank = element_size * num_elements_per_rank;

  void* buffer_data_at_rank_offset =
      (uint8_t*)buffer_data + buffer_len_per_rank * local_rank;

  int64_t num_elements_remaining = num_elements % local_size;

  void* buffer_data_remainder =
      (uint8_t*)buffer_data + buffer_len_per_rank * local_size;

  void* fused_input_data_remainder =
      (uint8_t*)fused_input_data + buffer_len_per_rank * local_size;

  const int root_rank = local_size - 1;

  const bool is_root_rank = local_rank == root_rank;

  const int64_t total_num_elements =
      is_root_rank ? num_elements_per_rank + num_elements_remaining
                   : num_elements_per_rank;

  if (num_elements_per_rank > 0) {
    // Lock addresses for reduction phase
    void* fused_input_data_locked;
    void* buffer_data_at_rank_offset_locked;

    // Lock input for reduce scatter
    hccl_result = hcclxLockDeviceAddress(const_cast<void*>(fused_input_data),
                                         &fused_input_data_locked);
    HCCL_OP_ASSERT(hcclSuccess == hccl_result);

    // Lock output for reduce scatter
    hccl_result =
        hcclxLockDeviceAddress(const_cast<void*>(buffer_data_at_rank_offset),
                               &buffer_data_at_rank_offset_locked);
    HCCL_OP_ASSERT(hcclSuccess == hccl_result);

    hccl_result = hcclReduceScatter(
        fused_input_data_locked, buffer_data_at_rank_offset_locked,
        (size_t)num_elements_per_rank,
        GetHCCLDataType(first_entry.tensor->dtype()), hcclSum,
        *op_context_.hccl_comm_, op_context_.collective_stream());
    HCCL_OP_ASSERT(hcclSuccess == hccl_result);

    hccl_result = hcclxUnlockDeviceAddress(fused_input_data_locked);
    HCCL_OP_ASSERT(hcclSuccess == hccl_result);

    hccl_result = hcclxUnlockDeviceAddress(buffer_data_at_rank_offset_locked);
    HCCL_OP_ASSERT(hcclSuccess == hccl_result);
  }

  if (num_elements_remaining > 0) {
    void* fused_input_data_remainder_locked;
    void* buffer_remainder_locked;

    // Lock input for reduce scatter
    hccl_result =
        hcclxLockDeviceAddress(const_cast<void*>(fused_input_data_remainder),
                               &fused_input_data_remainder_locked);
    HCCL_OP_ASSERT(hcclSuccess == hccl_result);

    // Lock output for reduce scatter
    hccl_result = hcclxLockDeviceAddress(
        const_cast<void*>(buffer_data_remainder), &buffer_remainder_locked);
    HCCL_OP_ASSERT(hcclSuccess == hccl_result);

    hccl_result = hcclReduce(
        fused_input_data_remainder_locked, buffer_remainder_locked,
        (size_t)num_elements_remaining,
        GetHCCLDataType(first_entry.tensor->dtype()), hcclSum, root_rank,
        *op_context_.hccl_comm_, op_context_.collective_stream());
    HCCL_OP_ASSERT(hcclSuccess == hccl_result);

    hccl_result = hcclxUnlockDeviceAddress(fused_input_data_remainder_locked);
    HCCL_OP_ASSERT(hcclSuccess == hccl_result);

    hccl_result = hcclxUnlockDeviceAddress(buffer_remainder_locked);
    HCCL_OP_ASSERT(hcclSuccess == hccl_result);
  }

  // * * * MPI PHASE * * *

  const size_t dtype_size = DataType_Size(first_entry.tensor->dtype());

  const size_t locally_reduced_host_buffer_size{(size_t)total_num_elements *
                                                dtype_size};
  void* locally_reduced_host_buffer_addr{nullptr};

  syn_status = synHostMalloc(device_id, locally_reduced_host_buffer_size, 0,
                             &locally_reduced_host_buffer_addr);
  HCCL_OP_ASSERT(synSuccess == syn_status);

  op_context_.CopyDataToHost(buffer_data_at_rank_offset,
                             locally_reduced_host_buffer_addr,
                             locally_reduced_host_buffer_size);
  op_context_.SynchronizeCurrentStream();
  timeline.ActivityEndAll(entries);
  timeline.ActivityStartAll(entries, MPI_ALLREDUCE);

  const int mpi_status = MPI_Allreduce(
      MPI_IN_PLACE, locally_reduced_host_buffer_addr, (int)total_num_elements,
      mpi_context_->GetMPIDataType(first_entry.tensor),
      mpi_context_->GetMPISumOp(first_entry.tensor->dtype()),
      mpi_context_->GetMPICommunicator(Communicator::CROSS));
  if (mpi_status != MPI_SUCCESS) {
    throw std::runtime_error(
        "MPI_Allreduce failed, see MPI output for details.");
  }

  timeline.ActivityEndAll(entries);
  timeline.ActivityStartAll(entries, HCCL_ALLGATHER);

  op_context_.CopyDataToDevice(locally_reduced_host_buffer_addr,
                               buffer_data_at_rank_offset,
                               locally_reduced_host_buffer_size);

  // * * * GATHERING PHASE * * *
  if (num_elements_per_rank > 0) {

    void* buffer_data_at_rank_offset_locked;
    void* buffer_data_locked;

    hccl_result =
        hcclxLockDeviceAddress(const_cast<void*>(buffer_data_at_rank_offset),
                               &buffer_data_at_rank_offset_locked);
    HCCL_OP_ASSERT(hcclSuccess == hccl_result);

    hccl_result = hcclxLockDeviceAddress(const_cast<void*>(buffer_data),
                                         &buffer_data_locked);
    HCCL_OP_ASSERT(hcclSuccess == hccl_result);

    hccl_result =
        hcclAllGather(buffer_data_at_rank_offset_locked, buffer_data_locked,
                      (size_t)num_elements_per_rank,
                      GetHCCLDataType(first_entry.tensor->dtype()),
                      *op_context_.hccl_comm_, op_context_.collective_stream());
    HCCL_OP_ASSERT(hcclSuccess == hccl_result);

    hccl_result = hcclxUnlockDeviceAddress(buffer_data_at_rank_offset_locked);
    HCCL_OP_ASSERT(hcclSuccess == hccl_result);

    hccl_result = hcclxUnlockDeviceAddress(buffer_data_locked);
    HCCL_OP_ASSERT(hcclSuccess == hccl_result);
  }

  if (num_elements_remaining > 0) {
    void* buffer_data_remainder_locked;
    hccl_result =
        hcclxLockDeviceAddress(const_cast<void*>(buffer_data_remainder),
                               &buffer_data_remainder_locked);
    HCCL_OP_ASSERT(hcclSuccess == hccl_result);

    hccl_result =
        hcclBcast(buffer_data_remainder_locked, num_elements_remaining,
                  GetHCCLDataType(first_entry.tensor->dtype()), root_rank,
                  *op_context_.hccl_comm_, op_context_.collective_stream());
    HCCL_OP_ASSERT(hcclSuccess == hccl_result);

    hccl_result = hcclxUnlockDeviceAddress(buffer_data_remainder_locked);
    HCCL_OP_ASSERT(hcclSuccess == hccl_result);
  }

  // TODO: [SW-45080] For unknown reason, a call to WaitForCompletion() is
  // necessary after Host->Device copy. This imposes a hard-barrier on the
  // execution's thread.
  if (fusion_buffer_in_use) {
    MemcpyOutFusionBuffer(buffer_data, entries);
  }

  return op_context_.FinalizeDeviceQueue(
      entries, [device_id, locally_reduced_host_buffer_addr] {
        // LOG(DEBUG) << "Freeing " << std::hex
        //           << (uint64_t)locally_reduced_host_buffer_addr <<
        // std::dec;
        synStatus syn_status =
            synHostFree(device_id, locally_reduced_host_buffer_addr, 0);
        HCCL_OP_ASSERT(synSuccess == syn_status);
        // locally_reduced_host_buffer is going out of scope.
      });
}

bool HCCLHierarchicalAllreduce::Enabled(
    const ParameterManager& param_manager,
    const std::vector<TensorTableEntry>& entries,
    const Response& response) const {
  if (!HCCLAllreduce::Enabled(param_manager, entries, response)) {
    return false;
  }
  return param_manager.HierarchicalAllreduce();
}

Status
HCCLHierarchicalBroadcast::Execute(std::vector<TensorTableEntry>& entries,
                                   const Response& response) {
  LOG(TRACE) << "Entry " << __PRETTY_FUNCTION__;

  op_context_.InitCommunicator(entries, response.devices());
  auto& timeline = global_state_->timeline;
  timeline.ActivityStartAll(entries, HCCL_BROADCAST);
  op_context_.InitDeviceQueue(entries,
                              op_context_.device_to_host_copy_stream());

  size_t required_buffer_size{0};
  auto& first_entry{entries[0]};

  const auto device_id = first_entry.device;

  auto mpi_rank{global_state_->global_controller->GetRank()};

  for (auto& entry : entries) {
    const bool is_root{mpi_rank == entry.root_rank};
    if (is_root) {
      required_buffer_size =
          (entry.tensor->size() > static_cast<int64_t>(required_buffer_size))
              ? entry.tensor->size()
              : required_buffer_size;
    } else {
      required_buffer_size =
          (entry.output->size() > static_cast<int64_t>(required_buffer_size))
              ? entry.output->size()
              : required_buffer_size;
    }
  }

  void* host_buffer_addr{nullptr};

  synStatus syn_status{
      synHostMalloc(device_id, required_buffer_size, 0, &host_buffer_addr)};
  HCCL_OP_ASSERT(synSuccess == syn_status);

  for (auto& entry : entries) {
    const bool is_root{mpi_rank == entry.root_rank};

    if (is_root) {
      op_context_.CopyDataToHost(const_cast<void*>(entry.tensor->data()),
                                 host_buffer_addr, entry.tensor->size());
      op_context_.SynchronizeCurrentStream();
    }
    const int mpi_status = MPI_Bcast(
        host_buffer_addr, entry.tensor->size(), MPI_CHAR, entry.root_rank,
        mpi_context_->GetMPICommunicator(Communicator::GLOBAL));
    if (mpi_status != MPI_SUCCESS) {
      throw std::runtime_error("MPI_BCast failed, see MPI output for details.");
    }

    if (!is_root) {
      op_context_.CopyDataToDevice(host_buffer_addr,
                                   const_cast<void*>(entry.output->data()),
                                   entry.tensor->size());
      op_context_.SynchronizeCurrentStream();
    }
  }

  syn_status = synHostFree(device_id, host_buffer_addr, 0);
  HCCL_OP_ASSERT(synSuccess == syn_status);

  return op_context_.FinalizeDeviceQueue(entries);
}

bool HCCLHierarchicalBroadcast::Enabled(
    const ParameterManager& param_manager,
    const std::vector<TensorTableEntry>& entries,
    const Response& response) const {
  if (!HCCLBroadcast::Enabled(param_manager, entries, response)) {
    return false;
  }
  return param_manager.HierarchicalAllreduce();
}

#endif // HAVE_MPI

} // namespace common
} // namespace horovod