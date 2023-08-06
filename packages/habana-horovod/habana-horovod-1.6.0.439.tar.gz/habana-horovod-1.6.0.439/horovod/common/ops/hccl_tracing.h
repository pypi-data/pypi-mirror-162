/*******************************************************************************
 * Copyright (C) 2022 Habana Labs, Ltd. an Intel Company
 * All Rights Reserved.
 *
 * Unauthorized copying of this file or any element(s) within it, via any medium
 * is strictly prohibited.
 * This file contains Habana Labs, Ltd. proprietary and confidential information
 * and is subject to the confidentiality and license agreements under which it
 * was provided.
 *
 *******************************************************************************
 */

#if HAVE_HCCL

// Currently HCCL is only supported for tf integration so it is not necessary to
// check for tensorflow specifically.
// In the future we might add some framework independent version (or just use
// empty one) for cases when tf tracing is not available.
#include <tensorflow/core/profiler/lib/traceme.h>

namespace horovod {
namespace common {

class TraceScope {
public:
  TraceScope(absl::string_view name, int level = 1) : t(name, level) {}

private:
  tensorflow::profiler::TraceMe t;
};

} // namespace common
} // namespace horovod

#define TRACE_SCOPE_UNIQ_HELPER(var, counter, name)                            \
  TraceScope var##counter { name }
#define TRACE_SCOPE(name)                                                      \
  TRACE_SCOPE_UNIQ_HELPER(_trace_scope_, __COUNTER__, name)
#else
#define TRACE_SCOPE(name)
#endif
