cimport iec61850_client

from libc.stdio cimport FILE, fopen, fwrite, fclose
from libc.stdint cimport uint8_t, uint32_t, uint64_t
from libcpp cimport bool
from cpython cimport int as py_int

import os
from enum import Enum


# Connection state of the IedConnection instance - either closed(idle), connecting, connected, or closing)
IED_STATE_CLOSED = iec61850_client.IedConnectionState.IED_STATE_CLOSED
IED_STATE_CONNECTING = iec61850_client.IedConnectionState.IED_STATE_CONNECTING
IED_STATE_CONNECTED = iec61850_client.IedConnectionState.IED_STATE_CONNECTED
IED_STATE_CLOSING = iec61850_client.IedConnectionState.IED_STATE_CLOSING


# Used to describe the error reason for most client side service functions
# general errors
IED_ERROR_OK = iec61850_client.IedClientError.IED_ERROR_OK
IED_ERROR_NOT_CONNECTED = iec61850_client.IedClientError.IED_ERROR_NOT_CONNECTED
IED_ERROR_ALREADY_CONNECTED = iec61850_client.IedClientError.IED_ERROR_ALREADY_CONNECTED
IED_ERROR_CONNECTION_LOST = iec61850_client.IedClientError.IED_ERROR_CONNECTION_LOST
IED_ERROR_SERVICE_NOT_SUPPORTED = iec61850_client.IedClientError.IED_ERROR_SERVICE_NOT_SUPPORTED
IED_ERROR_CONNECTION_REJECTED = iec61850_client.IedClientError.IED_ERROR_CONNECTION_REJECTED
IED_ERROR_OUTSTANDING_CALL_LIMIT_REACHED = iec61850_client.IedClientError.IED_ERROR_OUTSTANDING_CALL_LIMIT_REACHED

# client side errors
IED_ERROR_USER_PROVIDED_INVALID_ARGUMENT = iec61850_client.IedClientError.IED_ERROR_USER_PROVIDED_INVALID_ARGUMENT
IED_ERROR_ENABLE_REPORT_FAILED_DATASET_MISMATCH = iec61850_client.IedClientError.IED_ERROR_ENABLE_REPORT_FAILED_DATASET_MISMATCH
IED_ERROR_OBJECT_REFERENCE_INVALID = iec61850_client.IedClientError.IED_ERROR_OBJECT_REFERENCE_INVALID
IED_ERROR_UNEXPECTED_VALUE_RECEIVED = iec61850_client.IedClientError.IED_ERROR_UNEXPECTED_VALUE_RECEIVED

# service error - error reported by server
IED_ERROR_TIMEOUT = iec61850_client.IedClientError.IED_ERROR_TIMEOUT
IED_ERROR_ACCESS_DENIED = iec61850_client.IedClientError.IED_ERROR_ACCESS_DENIED
IED_ERROR_OBJECT_DOES_NOT_EXIST = iec61850_client.IedClientError.IED_ERROR_OBJECT_DOES_NOT_EXIST
IED_ERROR_OBJECT_EXISTS = iec61850_client.IedClientError.IED_ERROR_OBJECT_EXISTS
IED_ERROR_OBJECT_ACCESS_UNSUPPORTED = iec61850_client.IedClientError.IED_ERROR_OBJECT_ACCESS_UNSUPPORTED
IED_ERROR_TYPE_INCONSISTENT = iec61850_client.IedClientError.IED_ERROR_TYPE_INCONSISTENT
IED_ERROR_TEMPORARILY_UNAVAILABLE = iec61850_client.IedClientError.IED_ERROR_TEMPORARILY_UNAVAILABLE
IED_ERROR_OBJECT_UNDEFINED = iec61850_client.IedClientError.IED_ERROR_OBJECT_UNDEFINED
IED_ERROR_INVALID_ADDRESS = iec61850_client.IedClientError.IED_ERROR_INVALID_ADDRESS
IED_ERROR_HARDWARE_FAULT = iec61850_client.IedClientError.IED_ERROR_HARDWARE_FAULT
IED_ERROR_TYPE_UNSUPPORTED = iec61850_client.IedClientError.IED_ERROR_TYPE_UNSUPPORTED
IED_ERROR_OBJECT_ATTRIBUTE_INCONSISTENT = iec61850_client.IedClientError.IED_ERROR_OBJECT_ATTRIBUTE_INCONSISTENT
IED_ERROR_OBJECT_VALUE_INVALID = iec61850_client.IedClientError.IED_ERROR_OBJECT_VALUE_INVALID
IED_ERROR_OBJECT_INVALIDATED = iec61850_client.IedClientError.IED_ERROR_OBJECT_INVALIDATED
IED_ERROR_MALFORMED_MESSAGE = iec61850_client.IedClientError.IED_ERROR_MALFORMED_MESSAGE
IED_ERROR_SERVICE_NOT_IMPLEMENTED = iec61850_client.IedClientError.IED_ERROR_SERVICE_NOT_IMPLEMENTED

# unknown error
IED_ERROR_UNKNOWN = iec61850_client.IedClientError.IED_ERROR_UNKNOWN


# IedConnectionState dictionary
IED_CONNECTION_STATE = {
    IED_STATE_CLOSED: 'closed',
    IED_STATE_CONNECTING: 'connecting',
    IED_STATE_CONNECTED: 'connected',
    IED_STATE_CLOSING: 'closing'
}


#IedClientError dictionary
IED_CLIENT_ERROR = {
    # general errors
    IED_ERROR_OK: 'ok',
    IED_ERROR_NOT_CONNECTED: 'not connected',
    IED_ERROR_ALREADY_CONNECTED: 'already connected',
    IED_ERROR_CONNECTION_LOST: 'connection lost',
    IED_ERROR_SERVICE_NOT_SUPPORTED: 'service not supported',
    IED_ERROR_CONNECTION_REJECTED: 'connection rejected',
    IED_ERROR_OUTSTANDING_CALL_LIMIT_REACHED: 'outstanding call limit reached',
    
    # client side errors
    IED_ERROR_USER_PROVIDED_INVALID_ARGUMENT: 'user provided invalid argument',
    IED_ERROR_ENABLE_REPORT_FAILED_DATASET_MISMATCH: 'enabled report failed dataset mismatch',
    IED_ERROR_OBJECT_REFERENCE_INVALID: 'object reverence invalid',
    IED_ERROR_UNEXPECTED_VALUE_RECEIVED: 'unexpected value received',
    
    # service error - error reported by server
    IED_ERROR_TIMEOUT: 'timeout',
    IED_ERROR_ACCESS_DENIED: 'access denied',
    IED_ERROR_OBJECT_DOES_NOT_EXIST: 'object does not exist',
    IED_ERROR_OBJECT_EXISTS: 'object exists',
    IED_ERROR_OBJECT_ACCESS_UNSUPPORTED: 'object access unsupported',
    IED_ERROR_TYPE_INCONSISTENT: 'type inconsistent',
    IED_ERROR_TEMPORARILY_UNAVAILABLE: 'temporarily unavailable',
    IED_ERROR_OBJECT_UNDEFINED: 'object undefined',
    IED_ERROR_INVALID_ADDRESS: 'invalid address',
    IED_ERROR_HARDWARE_FAULT: 'hardware fault',
    IED_ERROR_TYPE_UNSUPPORTED: 'type unsupported',
    IED_ERROR_OBJECT_ATTRIBUTE_INCONSISTENT: 'object attribute inconsistent',
    IED_ERROR_OBJECT_VALUE_INVALID: 'object value invalid',
    IED_ERROR_OBJECT_INVALIDATED: 'object invalidated',
    IED_ERROR_MALFORMED_MESSAGE: 'malformed message',
    IED_ERROR_SERVICE_NOT_IMPLEMENTED: 'service not implemented',
    
    # unknown error
    IED_ERROR_UNKNOWN: 'unknown'
}

class connection_state(Enum):
    CLOSED = 0
    CONNECTING = 1
    CONNECTED = 2
    CLOSING = 3

class IedClientError(Enum):
    IED_ERROR_OK = 0
    IED_ERROR_NOT_CONNECTED = 1
    IED_ERROR_ALREADY_CONNECTED = 2
    IED_ERROR_CONNECTION_LOST = 3
    IED_ERROR_SERVICE_NOT_SUPPORTED = 4
    IED_ERROR_CONNECTION_REJECTED = 5
    IED_ERROR_OUTSTANDING_CALL_LIMIT_REACHED = 6
    IED_ERROR_USER_PROVIDED_INVALID_ARGUMENT = 10
    IED_ERROR_ENABLE_REPORT_FAILED_DATASET_MISMATCH = 11
    IED_ERROR_OBJECT_REFERENCE_INVALID = 12,
    IED_ERROR_UNEXPECTED_VALUE_RECEIVED = 13,
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


# Debug flag - print statements
DEBUG = 0


# add noexcept on the end of line bellow in Cython 3.x.x version
# cdef bool __downloadHandler(void* parameter, uint8_t* buffer, uint32_t bytesRead) noexcept:
cdef bool __downloadHandler(void* parameter, uint8_t* buffer, uint32_t bytesRead):
    """
    Download handler method
    
    Parameters
    ----------
    parameter : void *
        Pointer to 
    buffer : uint8_t
    bytesRead : uint32_t
    
    Returns
    -------
    status : bool
        True if writing is successful
    
    Raises
    ------
    IOError
        if failed to write local file
    """
    
    cdef FILE* fp = <FILE*> parameter
    if DEBUG:
        print('Received {} bytes'.format(bytesRead))
    
    if bytesRead > 0:
        if fwrite(buffer, bytesRead, 1, fp) != 1:
            if DEBUG:
                print('Failed to write local file')
            return False
    
    return True


cdef class IEC61850_client:
    cdef iec61850_client.IedConnection con
    cdef iec61850_client.IedClientError error
    cdef bytes hostname
    cdef int tcpPort
    
    
    def __init__(self):
        """
        Initialization method
        """
        
        self.create()
    
    
    def __dealoc__(self):
        """
        Dealocation method
        """
        
        self.destroy()
    
    
    cpdef void create(self):
        """
        Create a new IedConnection instance (extended version)
        
        This method creates a new instance that is used to handle a connection
        to an IED. It allocated all required resources. The new connection is
        in the "CLOSED" state. Before it can be used the connect method has to
        be called.
        
        Raises
        ------
        MemoryError
            if connection is not created due to insufficient memory
        """
        
        self.con = iec61850_client.IedConnection_create()
        
        if self.con is NULL:
            raise MemoryError()
    
    
    cpdef void destroy(self):
        """
        Destroy an IedConnection instance
        
        The connection will be closed if it is in "connected" state. All
        allocated resources of the connection will be freed.
        """
        
        iec61850_client.IedConnection_destroy(self.con)
    
    
    def set_connect_timeout(self, uint32_t timeout):
        """
        Set the connect timeout in ms for this connection
        
        NOTE: This function has to be called before connect method is called.
        
        Parameters
        ----------
        timeout : unit32_t
            Connect timeout in miliseconds
        """
        
        iec61850_client.IedConnection_setConnectTimeout(self.con, timeout)
    
    
    def set_request_timeout(self, uint32_t timeout = 5000):
        """
        Set the request timeout for this connection
        
        NOTE: This method can be called any time to adjust timeout behavior.
        
        Parameters
        ----------
        time : uint32_t
            Request timeout in miliseconds. Default 5000 ms
        """
        
        iec61850_client.IedConnection_setRequestTimeout(self.con, timeout)
    
    
    def get_request_timeout(self):
        """
        Get the request timeout for this connection
        
        Returns
        -------
        timeout : uint32_t
            Get request timeout in miliseconds. Default 5000 ms
        """
        
        return iec61850_client.IedConnection_getRequestTimeout(self.con)
    
    
    def connect(self, str hostname = 'localhost', int tcp_port = 102):
        """
        Creates connection to IED
        
        NOTE: Function will block until connection is up or timeout happened.
        
        Parameters
        ----------
        hostname : str
            IED hostname or IP address
        tcp_port : int
            IED MMS port
        
        Raises
        ------
        ConnectionError
            Connection was not established
        """
        
        self.hostname = hostname.encode()
        self.tcpPort = tcp_port
        
        iec61850_client.IedConnection_connect(self.con, &self.error, self.hostname, self.tcpPort)
        
        if self.error != IED_ERROR_OK:
            raise ConnectionError('Failed to connect to {}:{}: {} (code {})'.format(
                hostname,
                tcp_port,
                IED_CLIENT_ERROR[self.error].upper(),
                self.error))
    
    
    def abort(self):
        """
        Abort the connection
        
        This method will close the MMS association by sending an ACSE abort
        message to the server. After sending the abort message the connection
        is closed immediately. The client can assume the connection to be
        closed when the method returns and the destroy method can be called.
        If the connection is not in "connected" state an
        IED_ERROR_NOT_CONNECTED error will be reported.
        
        Raises
        ------
        ConnectionError
            Connection error - IED not connected
        """
        
        iec61850_client.IedConnection_abort(self.con, &self.error)
        
        if self.error != IED_ERROR_OK:
            raise ConnectionError('Connection error: {} (code {})'.format(
                IED_CLIENT_ERROR[self.error].upper(),
                self.error))
    
    
    def release(self):
        """
        Release the connection
        
        This method will release the MMS association by sending an MMS conclude
        message to the server. The client can NOT assume the connection to be
        closed when the function returns, It can also fail if the server
        returns with a negative response. To be sure that the connection will
        be closed the close or abort methods should be used.
        If the connection is not in "connected" state an
        IED_ERROR_NOT_CONNECTED error will be reported.
        
        Raises
        ------
        ConnectionError
            Connection error - IED not connected
        """
        
        iec61850_client.IedConnection_release(self.con, &self.error)
        
        if self.error != IED_ERROR_OK:
            raise ConnectionError('Connection error: {} (code {})'.format(
                IED_CLIENT_ERROR[self.error].upper(),
                self.error))
    
    
    def close(self):
        """
        Close the connection
        
        This function will close the MMS association and the underlying TCP
        connection.
        """
        
        iec61850_client.IedConnection_close(self.con)
    
    
    cdef iec61850_client.IedConnectionState get_state(self):
        """
        Return the state of the connection
        
        This function can be used to determine if the connection is established
        or closed.
        
        Return
        ------
        connection_state : IedConnectionState
            Return IedConnectionState enum
        """
        
        return iec61850_client.IedConnection_getState(self.con)
    
    
    def get_connection_state(self):
        """
        Return the state of the connection
        
        Return
        ------
        connection_state : str
            Return IED_CONNECTION_STATE dictionary value:
             - closed
             - connecting
             - connected
             - closing
        """
        
        return IED_CONNECTION_STATE[self.get_state()]
    
    
    def get_file_directory(self, str file_name=''):
        """
        Returns the directory entries of the specified file directory
        
        Parameters
        ----------
        file_name : str
            Specified file or directory.
            Default: '' (NONE) - root directory
        
        Returns
        -------
        file_list : list of tuples
            List of files (path, size, timestamp)
        
        Raises
        ------
        ConnectionError
            Error retriving file directory from IED
        """
        
        cdef iec61850_client.IedClientError error
        cdef iec61850_client.LinkedList rootDirectory
        cdef iec61850_client.LinkedList directoryEntry
        cdef iec61850_client.FileDirectoryEntry entry
        cdef bytes filename = file_name.encode()
        cdef str path
        cdef py_int size
        cdef py_int timestamp
        cdef list file_list = []
        
        rootDirectory = iec61850_client.IedConnection_getFileDirectory(self.con, &error, filename)
        
        if error != IED_ERROR_OK:
            raise ConnectionError('Error retrieving file directory: {} (code {})'.format(
                IED_CLIENT_ERROR[error].upper(),
                error))
        else:
            directoryEntry = iec61850_client.LinkedList_getNext(rootDirectory)
            
            while directoryEntry is not NULL:
                entry = <iec61850_client.FileDirectoryEntry> directoryEntry.data
                
                path = iec61850_client.FileDirectoryEntry_getFileName(entry).decode()
                size = iec61850_client.FileDirectoryEntry_getFileSize(entry)
                timestamp = iec61850_client.FileDirectoryEntry_getLastModified(entry)
                file_list.append((path, size, timestamp))
                if DEBUG:
                    print('%s %i %i' % (path, size, timestamp))
                
                directoryEntry = iec61850_client.LinkedList_getNext(directoryEntry)
            
            iec61850_client.LinkedList_destroyDeep(rootDirectory, <iec61850_client.LinkedListValueDeleteFunction> iec61850_client.FileDirectoryEntry_destroy)
        
        return file_list
    
    
    def get_file(self, str ied_file_name, str local_file_name=''):
        """
        Download the file from the server
        
        Parameters
        ----------
        ied_file_name : str
            IED file path (dirname + hostname)
        local_file_name : str
            Local file path (dirname + hostname).
            Defaults to IED hostname if local_file_name parameter is not set.
        
        Raises
        ------
        ConnectionError
            if file is not retrived from the IED
        IOError
            if local file can't be created or opened
        """
        
        cdef iec61850_client.IedClientError error
        cdef bytes iedFileName = ied_file_name.encode()
        cdef bytes localFileName = b''
        cdef FILE* fp
        
        # Create local file name
        if local_file_name:
            local_file = local_file_name
        else:
            local_file = os.path.basename(ied_file_name)
        
        # Create local file
        try:
            with open(local_file, 'x') as f:
                pass
        except:
            raise IOError('Failed to create local file {}'. format(local_file))
        
        # Create C pointer to local file and open file
        localFileName += local_file.encode()
        fp = fopen(localFileName, 'w')
        
        if fp is not NULL:
            # Download a file from the server
            iec61850_client.IedConnection_getFile(self.con, &error, iedFileName, __downloadHandler, <void*> fp)
            
            if error != IED_ERROR_OK:
                raise ConnectionError('Failed to get file {} from IED. {} (code {})'.format(
                    ied_file_name,
                    IED_CLIENT_ERROR[error].upper(),
                    error))
            
            fclose(fp)
        else:
            raise IOError('Failed to open local file {}'.format(local_file))
    
    
    def del_file(self, str file_name):
        """
        Delete the file from the server
        
        Parameters
        ----------
        file_name : str
            IED file path (dirname + hostname)
        
        Returns
        -------
        ConnectionError
            if file is not deleted from the IED
        """
        
        cdef iec61850_client.IedClientError error
        cdef bytes filename = file_name.encode()
        
        # Delete file from server
        iec61850_client.IedConnection_deleteFile(self.con, &error, filename);
        
        if error != IED_ERROR_OK:
            raise ConnectionError('Failed to delete file {} from IED. {} (code {})'.format(
                file_name,
                IED_CLIENT_ERROR[error].upper(),
                error))
    
    
    def set_file(self, src_file_name, dest_file_name=''):
        """
        Set the file to the server
        
        Parameters
        ----------
        src_file_name : str
            local file path (dirname + hostname)
        dest_file_name : str
            destination file name (dirname + hostname)
            Defaults to local hostname if dest_file_name parameter is not set.
        
        Returns
        -------
        ConnectionError
            if file is not set to the IED
        """
        
        cdef iec61850_client.IedClientError error
        
        # Source (local) file name (basename)
        cdef bytes sourceFilename = os.path.basename(src_file_name).encode()
        
        # Source (local) basepath (dirname)
        # IedConnection_setFilestoreBasepath requires the file separator at the end!
        cdef bytes basepath = os.path.dirname(src_file_name).encode()
        if dest_file_name.find('\\') != -1:
            basepath += '\\'.encode()
        else:
            basepath += '/'.encode()
        
        # Destination (IED) file path
        cdef bytes destinationFilename
        if not dest_file_name:
            destinationFilename = sourceFilename
        else:
            destinationFilename = dest_file_name.encode()
        
        # Set local basepath
        iec61850_client.IedConnection_setFilestoreBasepath(self.con, basepath)
        
        # Set file
        iec61850_client.IedConnection_setFile(self.con, &error, sourceFilename, destinationFilename)
        
        if error != IED_ERROR_OK:
            raise ConnectionError('Failed to set file {} to IED. {} (code {})'.format(
                src_file_name,
                IED_CLIENT_ERROR[error].upper(),
                error))
