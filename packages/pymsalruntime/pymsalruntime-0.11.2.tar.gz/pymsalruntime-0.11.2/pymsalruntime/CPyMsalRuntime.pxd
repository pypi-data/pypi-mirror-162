# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.

from libc.stdint cimport int32_t, int64_t, uint32_t

cdef extern from "./MSALRuntime.h" nogil:
    ctypedef Py_UNICODE utf16_char
    ctypedef utf16_char os_char

    ctypedef int bool_t

    cdef enum MSALRUNTIME_RESPONSE_STATUS:
        Msalruntime_Response_Status_Unexpected = 0
        Msalruntime_Response_Status_Reserved = 1
        Msalruntime_Response_Status_InteractionRequired = 2
        Msalruntime_Response_Status_NoNetwork = 3
        Msalruntime_Response_Status_NetworkTemporarilyUnavailable = 4
        Msalruntime_Response_Status_ServerTemporarilyUnavailable = 5
        Msalruntime_Response_Status_ApiContractViolation = 6
        Msalruntime_Response_Status_UserCanceled = 7
        Msalruntime_Response_Status_ApplicationCanceled = 8
        Msalruntime_Response_Status_IncorrectConfiguration = 9
        Msalruntime_Response_Status_InsufficientBuffer = 10
        Msalruntime_Response_Status_AuthorityUntrusted = 11
        Msalruntime_Response_Status_UserSwitch = 12
        Msalruntime_Response_Status_AccountUnusable = 13
        Msalruntime_Response_Status_UserDataRemovalRequired = 14
        Msalruntime_Response_Status_KeyNotFound = 15
        Msalruntime_Response_Status_AccountNotFound = 16

    cdef enum MSALRUNTIME_LOG_LEVEL:
        Msalruntime_Log_Level_Trace = 1
        Msalruntime_Log_Level_Debug = 2
        Msalruntime_Log_Level_Info = 3
        Msalruntime_Log_Level_Warning = 4
        Msalruntime_Log_Level_Error = 5
        Msalruntime_Log_Level_Fatal = 6

    cdef struct MSALRUNTIME_HANDLE:
        int unused

    ctypedef MSALRUNTIME_HANDLE* MSALRUNTIME_AUTH_PARAMETERS_HANDLE
    ctypedef MSALRUNTIME_HANDLE* MSALRUNTIME_AUTH_RESULT_HANDLE
    ctypedef MSALRUNTIME_HANDLE* MSALRUNTIME_SIGNOUT_RESULT_HANDLE
    ctypedef MSALRUNTIME_HANDLE* MSALRUNTIME_READ_ACCOUNT_RESULT_HANDLE
    ctypedef MSALRUNTIME_HANDLE* MSALRUNTIME_DISCOVER_ACCOUNTS_RESULT_HANDLE
    ctypedef MSALRUNTIME_HANDLE* MSALRUNTIME_ACCOUNT_HANDLE
    ctypedef MSALRUNTIME_HANDLE* MSALRUNTIME_ERROR_HANDLE
    ctypedef MSALRUNTIME_HANDLE* MSALRUNTIME_ASYNC_HANDLE
    ctypedef MSALRUNTIME_HANDLE* MSALRUNTIME_LOG_CALLBACK_HANDLE

    IF UNAME_SYSNAME == "Windows":
        ctypedef void (__stdcall *MSALRUNTIME_COMPLETION_ROUTINE)(
            MSALRUNTIME_AUTH_RESULT_HANDLE hResponse,
            void* callbackData)
        ctypedef void (__stdcall *MSALRUNTIME_SIGNOUT_COMPLETION_ROUTINE)(
            MSALRUNTIME_SIGNOUT_RESULT_HANDLE hResponse,
            void* callbackData)
        ctypedef void (__stdcall *MSALRUNTIME_READ_ACCOUNT_COMPLETION_ROUTINE)(
            MSALRUNTIME_READ_ACCOUNT_RESULT_HANDLE hResponse,
            void* callbackData)
        ctypedef void (__stdcall *MSALRUNTIME_DISCOVER_ACCOUNTS_COMPLETION_ROUTINE)(
            MSALRUNTIME_DISCOVER_ACCOUNTS_RESULT_HANDLE hResponse,
            void* callbackData)
        ctypedef void (__stdcall *MSALRUNTIME_LOG_CALLBACK_ROUTINE)(
            const os_char* logMessage,
            const MSALRUNTIME_LOG_LEVEL logLevel,
            void* callbackData)
        ctypedef void* WINDOW_HANDLE
        cdef extern from "Windows.h" nogil:
            WINDOW_HANDLE GetConsoleWindow()
            WINDOW_HANDLE GetDesktopWindow()
        cdef extern from "winuser.h" nogil:
            WINDOW_HANDLE GetAncestor(WINDOW_HANDLE hwnd, uint32_t gaFlags)
    ELSE:
        ctypedef void (*MSALRUNTIME_COMPLETION_ROUTINE)(
            MSALRUNTIME_AUTH_RESULT_HANDLE hResponse,
            void* callbackData)
        ctypedef void (*MSALRUNTIME_SIGNOUT_COMPLETION_ROUTINE)(
            MSALRUNTIME_SIGNOUT_RESULT_HANDLE hResponse,
            void* callbackData)
        ctypedef void (*MSALRUNTIME_READ_ACCOUNT_COMPLETION_ROUTINE)(
            MSALRUNTIME_READ_ACCOUNT_RESULT_HANDLE hResponse,
            void* callbackData)
        ctypedef void (*MSALRUNTIME_DISCOVER_ACCOUNTS_COMPLETION_ROUTINE)(
            MSALRUNTIME_DISCOVER_ACCOUNTS_RESULT_HANDLE hResponse,
            void* callbackData)
        ctypedef void (*MSALRUNTIME_LOG_CALLBACK_ROUTINE)(
            const os_char* logMessage,
            const MSALRUNTIME_LOG_LEVEL logLevel,
            void* callbackData)
        ctypedef int64_t WINDOW_HANDLE

    MSALRUNTIME_ERROR_HANDLE MSALRUNTIME_Startup()
    void MSALRUNTIME_Shutdown()

    MSALRUNTIME_ERROR_HANDLE MSALRUNTIME_CancelAsyncOperation(
        MSALRUNTIME_ASYNC_HANDLE asyncHandle
    )
    MSALRUNTIME_ERROR_HANDLE MSALRUNTIME_ReleaseAsyncHandle(MSALRUNTIME_ASYNC_HANDLE asyncHandle)

    MSALRUNTIME_ERROR_HANDLE MSALRUNTIME_ReadAccountByIdAsync(
        const os_char* accountId,
        const os_char* correlationId,
        MSALRUNTIME_READ_ACCOUNT_COMPLETION_ROUTINE callback,
        void* callbackData,
        MSALRUNTIME_ASYNC_HANDLE* asyncHandle)

    MSALRUNTIME_ERROR_HANDLE MSALRUNTIME_SignInAsync(
        WINDOW_HANDLE parentWindowHandle,
        MSALRUNTIME_AUTH_PARAMETERS_HANDLE authParameters,
        const os_char* correlationId,
        const os_char* accountHint,
        MSALRUNTIME_COMPLETION_ROUTINE callback,
        void* callbackData,
        MSALRUNTIME_ASYNC_HANDLE* asyncHandle)

    MSALRUNTIME_ERROR_HANDLE MSALRUNTIME_SignInSilentlyAsync(
        MSALRUNTIME_AUTH_PARAMETERS_HANDLE authParameters,
        const os_char* correlationId,
        MSALRUNTIME_COMPLETION_ROUTINE callback,
        void* callbackData,
        MSALRUNTIME_ASYNC_HANDLE* asyncHandle)

    MSALRUNTIME_ERROR_HANDLE MSALRUNTIME_SignInInteractivelyAsync(
        WINDOW_HANDLE parentWindowHandle,
        MSALRUNTIME_AUTH_PARAMETERS_HANDLE authParameters,
        const os_char* correlationId,
        const os_char* accountHint,
        MSALRUNTIME_COMPLETION_ROUTINE callback,
        void* callbackData,
        MSALRUNTIME_ASYNC_HANDLE* asyncHandle)

    MSALRUNTIME_ERROR_HANDLE MSALRUNTIME_AcquireTokenSilentlyAsync(
        MSALRUNTIME_AUTH_PARAMETERS_HANDLE authParameters,
        const os_char* correlationId,
        MSALRUNTIME_ACCOUNT_HANDLE account,
        MSALRUNTIME_COMPLETION_ROUTINE callback,
        void* callbackData,
        MSALRUNTIME_ASYNC_HANDLE* asyncHandle)

    MSALRUNTIME_ERROR_HANDLE MSALRUNTIME_AcquireTokenInteractivelyAsync(
        WINDOW_HANDLE parentWindowHandle,
        MSALRUNTIME_AUTH_PARAMETERS_HANDLE authParameters,
        const os_char* correlationId,
        MSALRUNTIME_ACCOUNT_HANDLE account,
        MSALRUNTIME_COMPLETION_ROUTINE callback,
        void* callbackData,
        MSALRUNTIME_ASYNC_HANDLE* asyncHandle)

    MSALRUNTIME_ERROR_HANDLE MSALRUNTIME_SignOutSilentlyAsync(
        const os_char* clientId,
        const os_char* correlationId,
        MSALRUNTIME_ACCOUNT_HANDLE account,
        MSALRUNTIME_SIGNOUT_COMPLETION_ROUTINE callback,
        void* callbackData,
        MSALRUNTIME_ASYNC_HANDLE* asyncHandle)

    MSALRUNTIME_ERROR_HANDLE MSALRUNTIME_DiscoverAccountsAsync(
        const os_char* clientId,
        const os_char* correlationId,
        MSALRUNTIME_DISCOVER_ACCOUNTS_COMPLETION_ROUTINE callback,
        void* callbackData,
        MSALRUNTIME_ASYNC_HANDLE* asyncHandle)

    MSALRUNTIME_ERROR_HANDLE MSALRUNTIME_RegisterLogCallback(
        MSALRUNTIME_LOG_CALLBACK_ROUTINE callback,
        void* callbackData,
        MSALRUNTIME_LOG_CALLBACK_HANDLE* callbackId)

    MSALRUNTIME_ERROR_HANDLE MSALRUNTIME_ReleaseLogCallbackHandle(MSALRUNTIME_LOG_CALLBACK_HANDLE callbackId)

    MSALRUNTIME_ERROR_HANDLE MSALRUNTIME_ReleaseAccount(MSALRUNTIME_ACCOUNT_HANDLE account)
    MSALRUNTIME_ERROR_HANDLE MSALRUNTIME_GetAccountId(
        MSALRUNTIME_ACCOUNT_HANDLE account,
        os_char* accountId,
        int32_t* bufferSize)
    MSALRUNTIME_ERROR_HANDLE MSALRUNTIME_GetClientInfo(
        MSALRUNTIME_ACCOUNT_HANDLE account,
        os_char* clientInfo,
        int32_t* bufferSize)
    MSALRUNTIME_ERROR_HANDLE MSALRUNTIME_GetAccountProperty(
        MSALRUNTIME_ACCOUNT_HANDLE account,
        const os_char* key,
        os_char* value,
        int32_t* bufferSize)

    MSALRUNTIME_ERROR_HANDLE MSALRUNTIME_CreateAuthParameters(
        const os_char* clientId,
        const os_char* authority,
        MSALRUNTIME_AUTH_PARAMETERS_HANDLE* authParameters)
    MSALRUNTIME_ERROR_HANDLE MSALRUNTIME_ReleaseAuthParameters(MSALRUNTIME_AUTH_PARAMETERS_HANDLE authParameters)
    MSALRUNTIME_ERROR_HANDLE MSALRUNTIME_SetRequestedScopes(
        MSALRUNTIME_AUTH_PARAMETERS_HANDLE authParameters,
        const os_char* scopes)
    MSALRUNTIME_ERROR_HANDLE MSALRUNTIME_SetRedirectUri(
        MSALRUNTIME_AUTH_PARAMETERS_HANDLE authParameters,
        const os_char* redirectUri)
    MSALRUNTIME_ERROR_HANDLE MSALRUNTIME_SetDecodedClaims(
        MSALRUNTIME_AUTH_PARAMETERS_HANDLE authParameters,
        const os_char* claims)
    MSALRUNTIME_ERROR_HANDLE MSALRUNTIME_SetAccessTokenToRenew(
        MSALRUNTIME_AUTH_PARAMETERS_HANDLE authParameters,
        const os_char* accessTokenToRenew)
    MSALRUNTIME_ERROR_HANDLE MSALRUNTIME_SetPopParams(
        MSALRUNTIME_AUTH_PARAMETERS_HANDLE authParameters,
        const os_char* httpMethod,
        const os_char* uriHost,
        const os_char* uriPath,
        const os_char* nonce)
    MSALRUNTIME_ERROR_HANDLE MSALRUNTIME_SetAdditionalParameter(
        MSALRUNTIME_AUTH_PARAMETERS_HANDLE authParameters,
        const os_char* key,
        const os_char* value)

    MSALRUNTIME_ERROR_HANDLE MSALRUNTIME_ReleaseAuthResult(MSALRUNTIME_AUTH_RESULT_HANDLE authResult)
    MSALRUNTIME_ERROR_HANDLE MSALRUNTIME_GetAccount(
        MSALRUNTIME_AUTH_RESULT_HANDLE authResult,
        MSALRUNTIME_ACCOUNT_HANDLE* account)
    MSALRUNTIME_ERROR_HANDLE MSALRUNTIME_GetIdToken(
        MSALRUNTIME_AUTH_RESULT_HANDLE authResult,
        os_char* IdToken,
        int32_t* bufferSize)
    MSALRUNTIME_ERROR_HANDLE MSALRUNTIME_GetRawIdToken(
        MSALRUNTIME_AUTH_RESULT_HANDLE authResult,
        os_char* RawIdToken,
        int32_t* bufferSize)
    MSALRUNTIME_ERROR_HANDLE MSALRUNTIME_GetAccessToken(
        MSALRUNTIME_AUTH_RESULT_HANDLE authResult,
        os_char* accessToken,
        int32_t* bufferSize)
    MSALRUNTIME_ERROR_HANDLE MSALRUNTIME_GetGrantedScopes(
        MSALRUNTIME_AUTH_RESULT_HANDLE authResult,
        os_char* grantedScopes,
        int32_t* bufferSize)
    MSALRUNTIME_ERROR_HANDLE MSALRUNTIME_GetAuthorizationHeader(
        MSALRUNTIME_AUTH_RESULT_HANDLE authResult,
        os_char* authHeader,
        int32_t* bufferSize)
    MSALRUNTIME_ERROR_HANDLE MSALRUNTIME_IsPopAuthorization(
        MSALRUNTIME_AUTH_RESULT_HANDLE authResult,
        bool_t* isPopAuthorization)
    MSALRUNTIME_ERROR_HANDLE MSALRUNTIME_GetExpiresOn(
        MSALRUNTIME_AUTH_RESULT_HANDLE authResult,
        int64_t* accessTokenExpirationTime)
    MSALRUNTIME_ERROR_HANDLE MSALRUNTIME_GetError(
        MSALRUNTIME_AUTH_RESULT_HANDLE authResult,
        MSALRUNTIME_ERROR_HANDLE* responseError)
    MSALRUNTIME_ERROR_HANDLE MSALRUNTIME_GetTelemetryData(
        MSALRUNTIME_AUTH_RESULT_HANDLE authResult,
        os_char* telemetryData,
        int32_t* bufferSize)

    MSALRUNTIME_ERROR_HANDLE MSALRUNTIME_ReleaseSignOutResult(MSALRUNTIME_SIGNOUT_RESULT_HANDLE signoutResult)
    MSALRUNTIME_ERROR_HANDLE MSALRUNTIME_GetSignOutError(
        MSALRUNTIME_SIGNOUT_RESULT_HANDLE signoutResult,
        MSALRUNTIME_ERROR_HANDLE* responseError)
    MSALRUNTIME_ERROR_HANDLE MSALRUNTIME_GetSignOutTelemetryData(
        MSALRUNTIME_SIGNOUT_RESULT_HANDLE signoutResult,
        os_char* telemetryData,
        int32_t* bufferSize)

    MSALRUNTIME_ERROR_HANDLE MSALRUNTIME_ReleaseReadAccountResult(MSALRUNTIME_READ_ACCOUNT_RESULT_HANDLE readAccountResult)
    MSALRUNTIME_ERROR_HANDLE MSALRUNTIME_GetReadAccount(
        MSALRUNTIME_READ_ACCOUNT_RESULT_HANDLE authResult,
        MSALRUNTIME_ACCOUNT_HANDLE* account)
    MSALRUNTIME_ERROR_HANDLE MSALRUNTIME_GetReadAccountError(
        MSALRUNTIME_READ_ACCOUNT_RESULT_HANDLE readAccountResult,
        MSALRUNTIME_ERROR_HANDLE* responseError)
    MSALRUNTIME_ERROR_HANDLE MSALRUNTIME_GetReadAccountTelemetryData(
        MSALRUNTIME_READ_ACCOUNT_RESULT_HANDLE readAccountResult,
        os_char* telemetryData,
        int32_t* bufferSize)

    MSALRUNTIME_ERROR_HANDLE MSALRUNTIME_ReleaseDiscoverAccountsResult(MSALRUNTIME_DISCOVER_ACCOUNTS_RESULT_HANDLE discoverAccountsResult)
    MSALRUNTIME_ERROR_HANDLE MSALRUNTIME_GetDiscoverAccountsAt(
        MSALRUNTIME_DISCOVER_ACCOUNTS_RESULT_HANDLE discoverAccountsResult,
        int32_t index,
        MSALRUNTIME_ACCOUNT_HANDLE* account)
    MSALRUNTIME_ERROR_HANDLE MSALRUNTIME_GetDiscoverAccountsError(
        MSALRUNTIME_DISCOVER_ACCOUNTS_RESULT_HANDLE discoverAccountsResult,
        MSALRUNTIME_ERROR_HANDLE* responseError)
    MSALRUNTIME_ERROR_HANDLE MSALRUNTIME_GetDiscoverAccountsTelemetryData(
        MSALRUNTIME_DISCOVER_ACCOUNTS_RESULT_HANDLE discoverAccountsResult,
        os_char* telemetryData,
        int32_t* bufferSize)

    bool_t MSALRUNTIME_ReleaseError(MSALRUNTIME_ERROR_HANDLE error)
    MSALRUNTIME_ERROR_HANDLE MSALRUNTIME_GetStatus(MSALRUNTIME_ERROR_HANDLE error, MSALRUNTIME_RESPONSE_STATUS* responseStatus)
    MSALRUNTIME_ERROR_HANDLE MSALRUNTIME_GetErrorCode(MSALRUNTIME_ERROR_HANDLE error, int64_t* responseError)
    MSALRUNTIME_ERROR_HANDLE MSALRUNTIME_GetTag(MSALRUNTIME_ERROR_HANDLE error, int32_t* responseErrorTag)
    MSALRUNTIME_ERROR_HANDLE MSALRUNTIME_GetContext(MSALRUNTIME_ERROR_HANDLE error, os_char* context, int32_t* bufferSize)
