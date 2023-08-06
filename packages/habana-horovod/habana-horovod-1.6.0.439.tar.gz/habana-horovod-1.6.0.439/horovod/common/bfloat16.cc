/******************************************************************************
 * Copyright (C) 2021 Habana Labs, Ltd. an Intel Company
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
#include "bfloat16.h"

namespace horovod {
namespace common {

#if HAVE_MPI
// bfloat16 custom data type summation operation.
void bfloat16_sum(void* invec, void* inoutvec, int* len,
                  MPI_Datatype* datatype) {
  const auto* in = reinterpret_cast<const uint16_t*>(invec);
  auto* inout = reinterpret_cast<uint16_t*>(inoutvec);
  const int length = *len;
  (void)datatype;

  for (int i = 0; i < length; ++i) {
    inout[i] = fp32_to_bf16(bf16_to_fp32(in[i]) + bf16_to_fp32(inout[i]));
  }
}
#endif

} // namespace common
} // namespace horovod
