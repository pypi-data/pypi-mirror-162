// Copyright 2016 The TensorFlow Authors. All Rights Reserved.
// Modifications copyright (C) 2019 Uber Technologies, Inc.
// Modifications copyright (C) 2020, NVIDIA CORPORATION. All rights reserved.
// Modifications copyright (C) 2021, Intel Corporation All rights reserved.
// Modifications copyright (C) 2022, HabanaLabs, Ltd. All rights reserved.
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

bool HCCLDummyAllreduce::Enabled(const ParameterManager& param_manager,
                                 const std::vector<TensorTableEntry>& entries,
                                 const Response& response) const {
  const bool is_enabled = ShouldSkipAllReduce() && !ShouldUseOrderedHccl();
  LOG(TRACE) << "HCCLDummyAllreduce is "
             << (is_enabled ? "enabled" : "disabled")
             << " for device: " << entries[0].device;
  return is_enabled;
}

Status HCCLDummyAllreduce::Execute(std::vector<TensorTableEntry>& entries,
                                   const Response& response) {
  LOG(TRACE) << "Entry " << __PRETTY_FUNCTION__;
  op_context_.InitCommunicator(entries, response.devices());

  auto& timeline = global_state_->timeline;
  timeline.ActivityStartAll(entries, HCCL_ALLREDUCE);

  const bool fusion_buffer_in_use{entries.size() > 1};
  auto& first_entry = entries[0];

  const void* fused_input_data;
  void* buffer_data{};
  size_t buffer_len{};

  op_context_.InitDeviceQueue(entries, op_context_.within_device_copy_stream());
  if (fusion_buffer_in_use) {
    MemcpyInFusionBuffer(entries, fused_input_data, buffer_data, buffer_len);
  } else {
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

  if (input_address == output_address) {
    LOG(DEBUG) << "Skipping inplace hcclAllreduce for num_elements="
               << (size_t)num_elements
               << " dtype=" << first_entry.tensor->dtype();
  } else {
    synStatus synapse_status = synMemCopyAsync(
        op_context_.within_device_copy_stream(),
        reinterpret_cast<uint64_t>(input_address), entries[0].tensor->size(),
        reinterpret_cast<uint64_t>(output_address), DRAM_TO_DRAM);
    HCCL_OP_ASSERT(synSuccess == synapse_status);
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

bool HCCLDummySignaledAllreduce::Enabled(
    const ParameterManager& param_manager,
    const std::vector<TensorTableEntry>& entries,
    const Response& response) const {
  const bool is_enabled = ShouldSkipAllReduce() && ShouldUseOrderedHccl();
  LOG(TRACE) << "HCCLDummySignaledAllreduce is "
             << (is_enabled ? "enabled" : "disabled")
             << " for device: " << entries[0].device;
  return is_enabled;
}

void HCCLDummySignaledAllreduce::ScheduleAllreduce(
    std::vector<TensorTableEntry>& entries, std::vector<int32_t>& device_map) {
  TRACE_SCOPE("HCCLDummySignaledAllreduce::ScheduleAllreduce");
  LOG(TRACE) << "Entry " << __PRETTY_FUNCTION__;

  op_context_.InitCommunicator(entries, device_map);
  auto& timeline = global_state_->timeline;
  timeline.ActivityStartAll(entries, HCCL_ALLREDUCE);

  // SFG allreduce is never done in place so there is not need for
  // copy elision here
  for (auto& entry : entries) {
    op_context_.InitDeviceQueue({entry},
                                op_context_.within_device_copy_stream());
    void* input_address;
    void* output_address;
    hcclResult_t hccl_result{hcclSuccess};

    hccl_result = hcclxLockDeviceAddress(
        const_cast<void*>(entry.tensor->data()), &input_address);
    HCCL_OP_ASSERT(hcclSuccess == hccl_result);
    hccl_result = hcclxLockDeviceAddress(
        const_cast<void*>(entry.output->data()), &output_address);
    HCCL_OP_ASSERT(hcclSuccess == hccl_result);

    auto copy_size{static_cast<uint64_t>(entry.tensor->size())};

    synStatus syn_status = synMemCopyAsync(
        op_context_.within_device_copy_stream(),
        reinterpret_cast<uint64_t>(input_address), copy_size,
        reinterpret_cast<uint64_t>(output_address), synDmaDir::DRAM_TO_DRAM);
    HCCL_OP_ASSERT(synSuccess == syn_status)

    hccl_result = hcclxUnlockDeviceAddress(input_address);
    HCCL_OP_ASSERT(hcclSuccess == hccl_result);
    hccl_result = hcclxUnlockDeviceAddress(output_address);
    HCCL_OP_ASSERT(hcclSuccess == hccl_result);
  }
}

} // namespace common
} // namespace horovod
