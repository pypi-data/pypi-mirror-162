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
#ifndef HOROVOD_BFLOAT16_H
#define HOROVOD_BFLOAT16_H

#include <cstdint>

#if HAVE_MPI
#define OMPI_SKIP_MPICXX
#include "mpi.h"
#endif

// During float32->bfloat16 conversion, prefer to round the value towards the
// nearest even. This is a compile-time decision.
#ifndef BFLOAT16_ROUND_NEAREST_EVEN
#define BFLOAT16_ROUND_NEAREST_EVEN true
#endif

namespace horovod {
namespace common {

union Data32 {
  uint32_t u32;
  float f;
};

inline float bf16_to_fp32(uint16_t v) {
  auto v_u32 = static_cast<uint32_t>(v) << 16;

  Data32 data32;
  data32.u32 = v_u32;
  return data32.f;
}

inline uint16_t fp32_to_bf16(float v) {
  Data32 data32;
  data32.f = v;
  uint32_t& v_u32 = data32.u32;

  if /*constexpr*/ (BFLOAT16_ROUND_NEAREST_EVEN) {
    // Rounding for all values except NaN & inf.
    const bool round = (v_u32 & 0x7f800000) != 0x7f800000 // not a inf/NaN
                       && v_u32 & 0x00008000              // ...and >=0.5
                       && v_u32 & 0x00017fff;             // ...and >5 or odd
    v_u32 += static_cast<uint32_t>(round) << 15;
  } else {
    const uint32_t exponent = (v_u32 & 0x7f800000u);
    if (exponent == 0) {
      v_u32 &= 0xff800000; // Flush to zero denormalized number.
    }
    // Proceed with rounding towards zero.
  }

  return static_cast<uint16_t>(v_u32 >> 16);
}

#if HAVE_MPI
void bfloat16_sum(void* invec, void* inoutvec, int* len,
                  MPI_Datatype* datatype);
#endif

} // namespace common
} // namespace horovod

#endif // HOROVOD_BFLOAT16_H
