from linked_list cimport *

from libc.stdint cimport uint8_t, uint32_t, uint64_t
from libcpp cimport bool


cdef extern from "iec61850_client.h":
    ##########################################################################
    # General client side connection handling functions and data types
    ##########################################################################
    
    # An opaque handle to the instance data of the IedConnection object
    ctypedef struct sIedConnection:
        pass
    
    ctypedef sIedConnection* IedConnection
    
    
    # Detailed description of the last application error of the client connection instance
    #typedef struct LastApplError:
    #    int ctlNum
    #    int error
    #    ControlAddCause addCause
    
    
    # Connection state of the IedConnection instance - either closed(idle), connecting, connected, or closing)
    ctypedef enum IedConnectionState:
        IED_STATE_CLOSED = 0,
        IED_STATE_CONNECTING,
        IED_STATE_CONNECTED,
        IED_STATE_CLOSING
    
    
    # used to describe the error reason for most client side service functions
    ctypedef enum IedClientError:
        # general errors
        IED_ERROR_OK = 0,
        IED_ERROR_NOT_CONNECTED = 1,
        IED_ERROR_ALREADY_CONNECTED = 2,
        IED_ERROR_CONNECTION_LOST = 3,
        IED_ERROR_SERVICE_NOT_SUPPORTED = 4,
        IED_ERROR_CONNECTION_REJECTED = 5,
        IED_ERROR_OUTSTANDING_CALL_LIMIT_REACHED = 6,
        
        # client side errors
        IED_ERROR_USER_PROVIDED_INVALID_ARGUMENT = 10,
        IED_ERROR_ENABLE_REPORT_FAILED_DATASET_MISMATCH = 11,
        IED_ERROR_OBJECT_REFERENCE_INVALID = 12,
        IED_ERROR_UNEXPECTED_VALUE_RECEIVED = 13,
        
        # service error - error reported by server
        IED_ERROR_TIMEOUT = 20,
        IED_ERROR_ACCESS_DENIED = 21,
        IED_ERROR_OBJECT_DOES_NOT_EXIST = 22,
        IED_ERROR_OBJECT_EXISTS = 23,
        IED_ERROR_OBJECT_ACCESS_UNSUPPORTED = 24,
        IED_ERROR_TYPE_INCONSISTENT = 25,
        IED_ERROR_TEMPORARILY_UNAVAILABLE = 26,
        IED_ERROR_OBJECT_UNDEFINED = 27,
        IED_ERROR_INVALID_ADDRESS = 28,
        IED_ERROR_HARDWARE_FAULT = 29,
        IED_ERROR_TYPE_UNSUPPORTED = 30,
        IED_ERROR_OBJECT_ATTRIBUTE_INCONSISTENT = 31,
        IED_ERROR_OBJECT_VALUE_INVALID = 32,
        IED_ERROR_OBJECT_INVALIDATED = 33,
        IED_ERROR_MALFORMED_MESSAGE = 34,
        IED_ERROR_SERVICE_NOT_IMPLEMENTED = 98,
        
        IED_ERROR_UNKNOWN = 99
    
    
    ###########################################################################
    # Connection creation and destruction
    ###########################################################################
    
    IedConnection IedConnection_create()
    
    # IedConnection IedConnection_createEx(TLSConfiguration tlsConfig, bool useThreads)
    
    # IedConnection IedConnection_createWithTlsSupport(TLSConfiguration tlsConfig)
    
    void IedConnection_destroy(IedConnection self)
    
    void IedConnection_setConnectTimeout(IedConnection self, uint32_t timeoutInMs)
    
    void IedConnection_setRequestTimeout(IedConnection self, uint32_t timeoutInMs)
    
    uint32_t IedConnection_getRequestTimeout(IedConnection self)
    
    bool IedConnection_tick(IedConnection self)
    
    ctypedef void (*IedConnection_GenericServiceHandler) (uint32_t invokeId, void* parameter, IedClientError err)
    
    
    ###########################################################################
    # Association service
    ###########################################################################
    
    void IedConnection_connect(IedConnection self, IedClientError* error, const char* hostname, int tcpPort)
    
    # void IedConnection_connectAsync(IedConnection self, IedClientError* error, const char* hostname, int tcpPort)
    
    void IedConnection_abort(IedConnection self, IedClientError* error)
    
    # void IedConnection_abortAsync(IedConnection self, IedClientError* error)
    
    void IedConnection_release(IedConnection self, IedClientError* error)
    
    # void IedConnection_releaseAsync(IedConnection self, IedClientError* error)
    
    void IedConnection_close(IedConnection self)
    
    IedConnectionState IedConnection_getState(IedConnection self)
    
    # LastApplError IedConnection_getLastApplError(IedConnection self)
    
    # ctypedef void (*IedConnectionClosedHandler) (void* parameter, IedConnection connection)
    
    # void IedConnection_installConnectionClosedHandler(IedConnection self, IedConnectionClosedHandler handler, void* parameter)
    
    # ctypedef void (*IedConnection_StateChangedHandler) (void* parameter, IedConnection connection, IedConnectionState newState)
    
    # IedConnection_installStateChangedHandler(IedConnection self, IedConnection_StateChangedHandler handler, void* parameter)
    
    # MmsConnection IedConnection_getMmsConnection(IedConnection self)
    
    
    ###########################################################################
    # File service related functions, data types, and definitions
    ###########################################################################
    
    ctypedef struct sFileDirectoryEntry:
        pass
    
    ctypedef sFileDirectoryEntry* FileDirectoryEntry
    
    void FileDirectoryEntry_destroy(FileDirectoryEntry self)
    
    const char* FileDirectoryEntry_getFileName(FileDirectoryEntry self)
    
    uint32_t FileDirectoryEntry_getFileSize(FileDirectoryEntry self)
    
    uint64_t FileDirectoryEntry_getLastModified(FileDirectoryEntry self)
    
    LinkedList IedConnection_getFileDirectory(IedConnection self, IedClientError* error, const char* directoryName)
    
    # LinkedList IedConnection_getFileDirectoryEx(IedConnection self, IedClientError* error, const char* directoryName, const char* continueAfter, bool* moreFollows)
    
    # ctypedef bool (*IedConnection_FileDirectoryEntryHandler) (uint32_t invokeId, void* parameter, IedClientError err, char* filename, uint32_t size, uint64_t lastModfified, bool moreFollows)
    
    # uint32_t IedConnection_getFileDirectoryAsyncEx(IedConnection self, IedClientError* error, const char* directoryName, const char* continueAfter, IedConnection_FileDirectoryEntryHandler handler, void* parameter)
    
    ctypedef bool (*IedClientGetFileHandler) (void* parameter, uint8_t* buffer, uint32_t bytesRead)
    
    uint32_t IedConnection_getFile(IedConnection self, IedClientError* error, const char* fileName, IedClientGetFileHandler handler, void* handlerParameter)
    
    # ctypedef bool (*IedConnection_GetFileAsyncHandler) (uint32_t invokeId, void* parameter, IedClientError err, uint32_t originalInvokeId, uint8_t* buffer, uint32_t bytesRead, bool moreFollows)
    
    # uint32_t IedConnection_getFileAsync(IedConnection self, IedClientError* error, const char* fileName, IedConnection_GetFileAsyncHandler handler, void* parameter)
    
    void IedConnection_setFilestoreBasepath(IedConnection self, const char* basepath)
    
    void IedConnection_setFile(IedConnection self, IedClientError* error, const char* sourceFilename, const char* destinationFilename)
    
    # uint32_t IedConnection_setFileAsync(IedConnection self, IedClientError* error, const char* sourceFilename, const char* destinationFilename, IedConnection_GenericServiceHandler handler, void* parameter)
    
    void IedConnection_deleteFile(IedConnection self, IedClientError* error, const char* fileName)
    
    # uint32_t IedConnection_deleteFileAsync(IedConnection self, IedClientError* error, const char* fileName, IedConnection_GenericServiceHandler handler, void* parameter)
