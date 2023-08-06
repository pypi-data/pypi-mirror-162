// Copyright (c) Microsoft Corporation.
// Licensed under the MIT License.

#pragma once

#ifdef __cplusplus
extern "C" {
#endif

/*
 * Releases the allocated MSALRUNTIME_ACCOUNT_HANDLE in the MSALRuntime.
 *
 * @in-param MSALRUNTIME_ACCOUNT_HANDLE account - the handle for the account.
 *
 * @return - success if null handle, otherwise fail.
 */
MSALRUNTIME_ERROR_HANDLE MSALRUNTIME_API MSALRUNTIME_ReleaseAccount(MSALRUNTIME_ACCOUNT_HANDLE account);

/*
 * Obtain the accountId from the account handle.
 *
 * @in-param MSALRUNTIME_ACCOUNT_HANDLE account - the handle for the account.
 * @out-param os_char* accountId - the buffer that is used to copy the accountId into.
 * @in-out-param int32_t* bufferSize - the size of the buffer (number of characters + null terminator).
 * It is updated by the method to indicate the actual size of the buffer.
 *
 * @return - null handle, success.
 * Handle with InsufficientBuffer status, if the buffer is too small, then bufferSize contains the new size to be
 * allocated. Otherwise fail.
 */
MSALRUNTIME_ERROR_HANDLE MSALRUNTIME_API
MSALRUNTIME_GetAccountId(MSALRUNTIME_ACCOUNT_HANDLE account, os_char* accountId, int32_t* bufferSize);

/*
 * Obtain the client info from the account handle.
 *
 * @in-param MSALRUNTIME_ACCOUNT_HANDLE account - the handle for the account.
 * @out-param os_char* clientInfo - the buffer that is used to copy the clientInfo into. This will be base64url encoded.
 * @in-out-param int32_t* bufferSize - the size of the buffer (number of characters + null terminator).
 * It is updated by the method to indicate the actual size of the buffer.
 *
 * @return - null handle, success.
 * Handle with InsufficientBuffer status, if the buffer is too small, then bufferSize contains the new size to be
 * allocated. Otherwise fail.
 */
MSALRUNTIME_ERROR_HANDLE MSALRUNTIME_API
MSALRUNTIME_GetClientInfo(MSALRUNTIME_ACCOUNT_HANDLE account, os_char* clientInfo, int32_t* bufferSize);

/*
 * Obtain the specified account Property from the account handle.
 *
 * @in-param MSALRUNTIME_ACCOUNT_HANDLE account - the handle for the account.
 * @in-param os_char* key - the key in the account properties to look for.
 * @out-param os_char* value - the value of the given key in the account properties.
 * @in-out-param int32_t* bufferSize - the size of the buffer (number of characters + null terminator).
 * It is updated by the method to indicate the actual size of the buffer.
 *
 * @return - null handle, success. If the bufferSize didn't update by this method, it means the key didn't find.
 * Handle with InsufficientBuffer status, if the buffer is too small, then bufferSize contains the new size to be
 * allocated. Otherwise fail.
 */
MSALRUNTIME_ERROR_HANDLE MSALRUNTIME_API
MSALRUNTIME_GetAccountProperty(MSALRUNTIME_ACCOUNT_HANDLE account, const os_char* key, os_char* value, int32_t* bufferSize);

#ifdef __cplusplus
}
#endif
