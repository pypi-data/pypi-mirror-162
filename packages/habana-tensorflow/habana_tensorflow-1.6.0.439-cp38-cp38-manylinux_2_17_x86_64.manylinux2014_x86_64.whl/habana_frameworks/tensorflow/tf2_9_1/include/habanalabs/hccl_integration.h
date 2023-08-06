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
 ******************************************************************************/

#pragma once

#include "hccl_types.h"

#ifdef __cplusplus
extern "C" {
#endif

// NOLINTNEXTLINE(modernize-use-using)
typedef void* hcclxCallbackCookie_t;
// NOLINTNEXTLINE(modernize-use-using)
typedef void (*hcclxCallback_t)(hcclxCallbackCookie_t);

/* Memory copy types */
// NOLINTNEXTLINE(modernize-use-using)
typedef enum {
  hcclxMemcpyHostToHost = 0,
  hcclxMemcpyHostToDevice = 1,
  hcclxMemcpyDeviceToHost = 2,
  hcclxMemcpyDeviceToDevice = 3,
  hcclxMemcpyDefault = 4,
  hcclxNumMemcpyKindTypes
} hcclxMemcpyKind_t;

hcclResult_t hcclxCreateDevice(int ordinal, int* device_id_ptr);

hcclResult_t hcclxCloseDevice(int device_id);

hcclResult_t hcclxOpenDevice(int device_id);

hcclResult_t hcclxSetDevice(int device_id);

hcclResult_t hcclxLockDeviceAddress(void* const address, void** device_address);

hcclResult_t hcclxUnlockDeviceAddress(void* const device_address);

hcclResult_t hcclxAcquireCollectiveStream(int device_id, synStreamHandle* stream_handle);

hcclResult_t hcclxReleaseCollectiveStream(synStreamHandle stream_handle);

hcclResult_t hcclxAcquireCopyStream(int device_id, synStreamHandle* stream_handle_ptr, hcclxMemcpyKind_t kind);

hcclResult_t hcclxReleaseCopyStream(synStreamHandle stream_handle);

hcclResult_t hcclxMalloc(void** address_ptr, size_t size);

hcclResult_t hcclxFree(void* address);

hcclResult_t hcclxMemcpySync(void* dst_device_address, const void* src_device_address, size_t size,
                             hcclxMemcpyKind_t kind);

hcclResult_t hcclxPrepareStream(synStreamHandle stream_handle, void** input_addresses_array_ptr, size_t array_length);

hcclResult_t hcclxSubmitEvents(synStreamHandle stream_handle, void** input_addresses_array_ptr, size_t array_length,
                               hcclxCallback_t cleanup_callback, hcclxCallbackCookie_t callback_cookie);

hcclResult_t hcclxStreamSynchronize(synStreamHandle stream_handle);

hcclResult_t hcclxGetExecutionOrder(int64_t order_id, int64_t* execution_order);

#ifdef __cplusplus
}  // extern "C"
#endif
