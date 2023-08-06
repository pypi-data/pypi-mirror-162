#include <absl/memory/memory.h>
#include <synapse_api.h>

#include "hccl_tracing.h"

#include "hccl_integration.h"
#include "hccl_operations.h"

namespace horovod {
namespace common {

OrderingGroup&
OrderedOpContext::GetOrderingGroup(const std::set<int>& ordering_indices,
                                   std::vector<int32_t> device_map) {
  TRACE_SCOPE("OrderedOpContext::GetOrderingGroup");
  if (ordering_groups_.end() == ordering_groups_.find(ordering_indices)) {
    OrderingGroup ordering_group(ordering_indices.size(), device_map);
    ordering_groups_.emplace(
        std::make_pair(ordering_indices, std::move(ordering_group)));
  }
  return ordering_groups_.at(ordering_indices);
}

void OrderedOpContext::RemoveOrderingGroupIfCompleted(
    const std::set<int>& indices) {
  TRACE_SCOPE("OrderedOpContext::RemoveOrderingGroupIfCompleted");
  // TODO: find
  if (ordering_groups_.at(indices).group_completed()) {
    ordering_groups_.erase(indices);
  }
}

void OrderingGroup::AddEntry(TensorTableEntry&& entry) {
  TRACE_SCOPE("OrderingGroup::AddEntry");
  int64_t order_index = entry.order_index;
  int64_t execution_order;
  // TODO: group should be stored per device list

  if (0 == ordered_queue_.size()) {
    // This routine creates empty ordered_queue_, will be called once
    // every iteration

    TRACE_SCOPE("Prepearing fresh ordered queue.");
    // Step zero: resize ordered vector of tensor descriptors
    ordered_queue_.resize(group_size_);
    // Step one: Insert all the keys to set with custom
    // comparator, so keys will be sorted on insertion.
    // As a key we are using pair of order index and execution order
    // value returned from synapse.
    std::set<OrderingKey, OrderingKeyCompare> q;
    for (int64_t new_order_index : entry.group_order_indices) {
      hcclResult_t hcclx_result{
          hcclxGetExecutionOrder(new_order_index, &execution_order)};
      HCCL_OP_ASSERT(hcclSuccess == hcclx_result);
      LOG(TRACE) << "Execution order for order_index " << new_order_index
                 << " is " << execution_order;
      q.insert({new_order_index, execution_order});
    }

    // Step two: Iterate over set, and associate each order_index (identifies
    // op) with place on ordered_queue_.
    int list_index = 0;
    order_index_to_list_index_.clear();
    for (const OrderingKey& q_key : q) {
      order_index_to_list_index_[q_key.first] = list_index;
      ordered_queue_[list_index].key = q_key;
      list_index++;
    }
  }

  // Now once we are sure that underlying structure exists lets fill item
  // descriptor for correct place in ordered list.
  const int list_index{order_index_to_list_index_[order_index]};
  LOG(TRACE) << "Adding entry with order index: " << order_index;
  ordered_queue_[list_index].tensor_entry = std::move(entry);
  ordered_queue_[list_index].ready = true;
  ordered_queue_[list_index].sent = false;
}

int OrderingGroup::ShouldWaitForMoreEntries(int requested_batch_size) {
  TRACE_SCOPE("OrderingGroup::ShouldWaitForMoreEntries");
  int max_possible_batch_size{0};
  bool all_items_ready{true};
  for (size_t ii = queue_items_sent_; ii < ordered_queue_.size(); ii++) {
    const QueueEntry& item = ordered_queue_[ii];
    if (!item.ready) {
      all_items_ready = false;
      break;
    }

    if (item.sent) {
      continue;
    }

    max_possible_batch_size += item.tensor_entry.tensor->size();
  }

  LOG(TRACE) << "There is " << max_possible_batch_size
             << " bytes of data available.";
  // We should wait when:
  // - we do not have requested batch to submit (so we are waiting for more
  // items)
  // - there will be more items available in the future
  return !all_items_ready && requested_batch_size > max_possible_batch_size;
}

std::vector<TensorTableEntry> OrderingGroup::GetEntriesToSchedule() {
  TRACE_SCOPE("OrderingGroup::GetEntriesToSchedule");
  LOG(TRACE) << __PRETTY_FUNCTION__;
  std::vector<TensorTableEntry> entries;

  const size_t ordering_queue_size{ordered_queue_.size()};
  entries.reserve(ordering_queue_size);

  const int min_batch_size{
      HcclSignalingFromEncapOpMinBatchSize()}; // 0 for no limit

  LOG(TRACE) << "Batch size for signaling is set to: " << min_batch_size << ".";

  if (0 != min_batch_size && ShouldWaitForMoreEntries(min_batch_size)) {
    LOG(TRACE) << "Not enough tensors ready to meet requested batch size.";
    return entries;
  }

  int current_batch_size = 0;
  for (size_t ii = queue_items_sent_; ii < ordered_queue_.size(); ii++) {
    QueueEntry& item = ordered_queue_[ii];
    if (!item.ready) {
      LOG(INFO) << "Waiting for item with order index " << item.key.first
                << " execution order " << item.key.second;
      break;
    }

    if (item.sent) {
      continue;
    }

    current_batch_size += item.tensor_entry.tensor->size();

    entries.push_back(std::move(item.tensor_entry));

    item.sent = true;
    queue_items_sent_++;
    LOG(INFO) << "Marking as sent. order index: " << item.key.first
              << " exec order: " << item.key.second;

    if (min_batch_size > 0 && current_batch_size >= min_batch_size) {
      LOG(INFO) << "Signaled op batch size limit is reached: " << entries.size()
                << " entries to schedule. Current batch size: "
                << current_batch_size;
      break;
    }
  }

  return entries;
}

Status HCCLSignaledAllreduce::Execute(std::vector<TensorTableEntry>& entries,
                                      const Response& response) {
  TRACE_SCOPE("HCCLSignaledAllreduce::Execute");
  LOG(TRACE) << "Entry " << __PRETTY_FUNCTION__;
  std::lock_guard<std::mutex> execute_guard(execute_mutex_);
  auto& timeline = global_state_->timeline;

  timeline.ActivityStartAll(entries, HCCL_REORDERING);

  HCCL_OP_ASSERT(entries.size() == 1);

  auto entry = std::move(entries[0]);
  std::set<int> indices = entry.group_order_indices;
  Status hvd_status{Status::InProgress()};

  {
    auto& ordering_group{
        ordered_op_context_.GetOrderingGroup(indices, response.devices())};
    ordering_group.AddEntry(std::move(entry));
    entries.clear();

    std::vector<TensorTableEntry> entries_to_schedule{
        ordering_group.GetEntriesToSchedule()};

    while (entries_to_schedule.size() > 0) {
      timeline.ActivityEndAll(entries_to_schedule);
      ScheduleAllreduce(entries_to_schedule, ordering_group.device_map());
      hvd_status = op_context_.FinalizeDeviceQueue(entries_to_schedule);
      entries_to_schedule = ordering_group.GetEntriesToSchedule();
    }
  }
  ordered_op_context_.RemoveOrderingGroupIfCompleted(indices);
  return hvd_status;
}

void HCCLSignaledAllreduce::ScheduleAllreduce(
    std::vector<TensorTableEntry>& entries, std::vector<int32_t>& device_map) {
  TRACE_SCOPE("HCCLSignaledAllreduce::ScheduleAllreduce");
  LOG(TRACE) << "Entry " << __PRETTY_FUNCTION__;

  op_context_.InitCommunicator(entries, device_map);
  auto& timeline = global_state_->timeline;
  timeline.ActivityStartAll(entries, HCCL_ALLREDUCE);

  for (auto& entry : entries) {
    op_context_.InitDeviceQueue({entry}, op_context_.collective_stream());
    void* input_address;
    void* output_address;
    hcclResult_t hccl_result{hcclSuccess};

    hccl_result = hcclxLockDeviceAddress(
        const_cast<void*>(entry.tensor->data()), &input_address);
    HCCL_OP_ASSERT(hcclSuccess == hccl_result);
    hccl_result = hcclxLockDeviceAddress(
        const_cast<void*>(entry.output->data()), &output_address);
    HCCL_OP_ASSERT(hcclSuccess == hccl_result);

    hccl_result =
        hcclAllReduce(input_address, output_address,
                      (size_t)entry.tensor->shape().num_elements(),
                      GetHCCLDataType(entry.tensor->dtype()), hcclSum,
                      *op_context_.hccl_comm_, op_context_.collective_stream());

    hccl_result = hcclxUnlockDeviceAddress(input_address);
    HCCL_OP_ASSERT(hcclSuccess == hccl_result);
    hccl_result = hcclxUnlockDeviceAddress(output_address);
    HCCL_OP_ASSERT(hcclSuccess == hccl_result);
  }
}

bool HCCLSignaledAllreduce::Enabled(
    const ParameterManager& param_manager,
    const std::vector<TensorTableEntry>& entries,
    const Response& response) const {
  bool is_enabled =
      (entries[0].device != CPU_DEVICE_ID) && ShouldUseOrderedHccl();
  LOG(TRACE) << "HCCLAllreduce is " << (is_enabled ? "enabled" : "disabled")
             << " for device: " << entries[0].device;
  return is_enabled;
}

} // namespace common
} // namespace horovod
