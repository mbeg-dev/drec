import os
import shutil
import logging
import traceback
import time

# Import FTP
import ftplib

# Import from common
from ..common import str_to_timestamp
from ..common import is_downloaded
from ..common import group_dev_file_list
from ..common import get_trigger_time
from ..common import dir_list_diff
from ..common import file_attr_format_str_len


# Set logger name to module name
logger = logging.getLogger('drec.ftp')


class FTPClient(ftplib.FTP):
    """
    Class for disturbance record download via FTP
    """
    
    def __init__(self, interrupt):
        """
        Initialization
        
        Parameters
        ----------
        interrupt : threading.Event.Event() object
            Event() object from threading.Event library used to gracefully
            terminate program
        """
        
        # Initialize child class
        super().__init__()
        
        # Interrupts - threading.Event - Event()
        self._interrupt = interrupt
    
    
    def download(self, dev_address, local_dirname, dev_dir='COMTRADE', dev_port=21, user='anonymous', password='', con_timeout=30, poll_timeout=0, ret_timeout=10, no_retry=1, dev_tz='UTC', local_tz='UTC'):
        """
        Download disturbance records
        
        Parameters
        ----------
        dev_address : str
            Device IP address or hostname
        local_dirname : str
            Path to local storage directory
        dev_dir : str
            Device directory path for disturbance records
        dev_port : int
            Device port. Default is 21
        user : str
            FTP server username. Default is anonymous
        password : str
            FTP server password. Default is empty passowrd
        con_timeout : int
            Connection timeout. Default is 30 s
        poll_timeout : int
            Timeout between polling requests in seconds. Default is 0 s
        ret_timeout : int
            Retry timeout in seconds. Default is 10 s
        no_retry : int
            Number of retries after error. Default 1
        dev_tz : str
            Device timezone. Default is UTC
        local_tz : str
            Local timezone. Default is UTC
        
        Note
        ----
        List of tz database time zones
        https://en.wikipedia.org/wiki/List_of_tz_database_time_zones
        """
        
        # Download counter for poll timeout
        download_count = 0
        
        for attempt in range(no_retry + 1):
            # Remove .tmp directory
            local_tmp_dirname = os.path.join(local_dirname, '.tmp')
            if os.path.isdir(local_tmp_dirname):
                shutil.rmtree(local_tmp_dirname)
            
            try:
                # Check interrupt flag and exit if necesary
                if self._interrupt.is_set(): break
                
                # Connect to device
                if self.get_connection_state() != 'connected':
                    self.connect(dev_address, port=dev_port, timeout=con_timeout)
                    self.login(user=user, passwd=password)
                    logger.debug('Connected to %s:%s', dev_address, dev_port)
                
                # Check interrupt flag and exit if necesary
                if self._interrupt.is_set(): break
                
                # Set the current directory on the FTP server
                self.cwd(dev_dir)
                
                # Download file directory
                dev_file_list = self.get_file_directory(dev_tz)
                
                # Formated file structure output
                
                # Get string lengths for formated file structure
                format_str_len = file_attr_format_str_len(dev_file_list)
                
                # Print header
                logger.debug('IED file structure:')
                format_str = '%-{}s%{}s%{}s'.format(*format_str_len)
                logger.debug(format_str, 'NAME', 'SIZE', 'TIME')
                logger.debug('-' * sum(format_str_len))
                
                # Print file attributes
                format_str = '%-{}s%{}d%{}.3f'.format(*format_str_len)
                for f in dev_file_list:
                    logger.debug(format_str, *f)
                
                # Check interrupt flag and exit if necesary
                if self._interrupt.is_set(): break
                
                # Loop through disturbance records (filter, order, group the list)
                for dist_rec in group_dev_file_list(dev_file_list, ''):
                    # Check interrupt flag and exit if necesary
                    if self._interrupt.is_set(): break
                    
                    # Check if files are already downloaded
                    # If files are not downloaded set download to True
                    download = False
                    for dev_path, dev_size, dev_timestamp in dist_rec:
                        if not is_downloaded(dev_path, local_dirname):
                            download = True
                            break
                    
                    if download and not self._interrupt.is_set():
                        # Create .tmp dir if it doesn't exist
                        os.makedirs(local_tmp_dirname, mode=0o700, exist_ok=True)
                        
                        # Loop through files and download them
                        for dev_path, dev_size, dev_timestamp in dist_rec:
                            # Extract basename and dirname from path
                            dev_basename = os.path.basename(dev_path)
                            dev_dirname = os.path.dirname(dev_path)
                            
                            # Local download path to .tmp directory
                            local_path = os.path.join(local_tmp_dirname, dev_basename)
                            
                            # Polling timeout
                            if download_count > 0:
                                if poll_timeout > 0:
                                    logger.debug('Poll timeout: {} s'.format(poll_timeout))
                                self._interrupt.wait(poll_timeout)
                            
                            # Check interrupt flag and exit if necesary
                            #if self._interrupt.is_set(): break
                            
                            # Download disturbance record
                            logger.debug('Started downloading: %s %s', dev_address, dev_path)
                            self.retr(dev_path, local_path)
                            logger.debug('Downloaded: %s %s -> %s', dev_address, dev_path, local_path)
                            
                            # Set local timestamp
                            os.utime(local_path, (dev_timestamp, dev_timestamp))
                            
                            # Increase download count for poll request
                            download_count += 1
                        
                        # Move downloaded files from .tmp to parent local directory
                        # Read comtrade file and find trigger_time
                        trigger_time = get_trigger_time(os.path.join(local_tmp_dirname, os.path.basename(dist_rec[0][0])), tz=local_tz)
                        
                        # Copy files with attributes (such as timestamp) and add date as filename prefix
                        tmp_files = (f for f in os.listdir(local_tmp_dirname) if os.path.isfile(os.path.join(local_tmp_dirname, f)))
                        for basename in tmp_files:
                            local_file = os.path.join(local_dirname, trigger_time + '_' + basename)
                            local_tmp_file = os.path.join(local_tmp_dirname, basename)
                            shutil.copy2(local_tmp_file, local_file)
                            logger.info('Downloaded: %s %s -> %s', dev_address, basename, local_file)
                        
                        # Delete .tmp directory with all files
                        shutil.rmtree(local_tmp_dirname)
                
                # Check interrupt flag and exit if necesary
                if self._interrupt.is_set(): break
                
                # Compare list of local files with list of device disturbance record files and search for differences
                # Move local disturbance records which do not exist in device anymore to archive directory
                archive_path = os.path.join(local_dirname, 'archive')

                # dir_list_diff for FTP protocol uses empty directory string (dev_dir = '') since FTP uses
                # relative path and download directory must be set before browsing or downloading files
                for f in dir_list_diff(dev_file_list, local_dirname, ''):
                    os.makedirs(archive_path, mode=0o755, exist_ok=True)
                    logger.debug('Moving to archive: %s', f)
                    shutil.move(f, os.path.join(archive_path, os.path.basename(f)))
                
                # Break the retry loop if code is executed without errors
                break
            
            except ConnectionError as err:
                logger.error(err)
                
                if attempt < no_retry:
                    # Retry for connection error
                    # Close connection
                    self.quit()
                    logger.debug('Disconnected from %s:%s', dev_address, dev_port)
                    
                    # Retry timeout
                    if ret_timeout > 0:
                        logger.debug('Retry timeout: {} s'.format(ret_timeout))
                        self._interrupt.wait(ret_timeout)
                    
                    continue
                else:
                    # Max retry attempts
                    logger.warning('Max retry attempts %s', dev_address)
                    break
            
            except ftplib.all_errors as err:
                logger.error(err)
                
                if attempt < no_retry:
                    # Retry for connection error
                    # Close connection
                    try:
                        # Close connection politely
                        self.quit()
                    except:
                        # Close connection unilaterally
                        self.close()
                    logger.debug('Disconnected from %s:%s', dev_address, dev_port)
                    
                    # Retry timeout
                    if ret_timeout > 0:
                        logger.debug('Retry timeout: {} s'.format(ret_timeout))
                        self._interrupt.wait(ret_timeout)
                    
                    continue
                else:
                    # Max retry attempts
                    logger.warning('Max retry attempts %s', dev_address)
                    break
            
            except:
                # Log message and close connection to device
                logger.critical('Fatal error %s: %s', dev_address, traceback.format_exc())
                break
        
        # Close connection
        try:
            # Close connection politely
            self.quit()
        except:
            # Close connection unilaterally
            self.close()
        logger.debug('Disconnected from %s:%s', dev_address, dev_port)
    
    
    def mdtm(self, filename):
        """
        MDTM FTP command
        
        Return the last-modified time of a specified file
        
        Parameters
        ----------
        filename : str
            Server file name
        
        Returns
        -------
        timestamp : str
            timestamp in format YYYYMMDDHHMMSS
        """
        
        self.voidcmd('MDTM ' + filename)[4:].strip()
    
    
    def retr(self, file_name, local_file_name=''):
        """
        RETR FTP command
        
        Download the file from the server
        
        Parameters
        ----------
        file_name : str
            FTP server file name (hostname)
        local_file_name : str
            Local file path (dirname + hostname).
            Defaults to FTP server hostname if local_file_name parameter is not
            set.
        """
        
        # Set local file name if it's not set
        if not local_file_name:
            local_file_name = os.path.basename(file_name)
        
        # Download file
        with open(local_file_name, 'wb') as f:
            ret = self.retrbinary('RETR ' + file_name, f.write)
    
    
    def noop(self):
        """
        NOOP FTP command
        
        No Operation
        
        This command does not affect anything at all. It performs no action
        other than having the server send an OK reply. This command is used
        to keep connections with servers "alive" (connected) while nothing
        is being done.
        """
        
        self.voidcmd('NOOP')
    
    
    def get_connection_state(self):
        """
        Return the state of the connection
        
        This function can be used to determine if the connection is established
        or closed using NOOP command.
        
        Return
        ------
        connection_state : str
            Return connected or closed
        """
        
        try:
            self.noop()
            return 'connected'
        except:
            return 'closed'
    
    
    def get_file_directory(self, dev_tz='UTC'):
        """
        Returns the directory entries of the current directory on the server
        
        Returns
        -------
        file_list : list of tuples
            List of files (path, size, timestamp)
        dev_tz : str
            Device time zone. Default is UTC
        
        Raises
        ------
        ConnectionError
            error retriving file directory from device
        
        Notes
        -----
        List of tz database time zones
        https://en.wikipedia.org/wiki/List_of_tz_database_time_zones
        """
        
        file_list = []
        current_time = time.time()
        
        # SIZE command error counter
        error_count_SIZE = 0
        MAX_ERROR_COUNT_SIZE = 2
        
        # MDTM command error counter
        error_count_MDTM = 0
        MAX_ERROR_COUNT_MDTM = 2
        
        try:
            # Get list of files with MLSD command
            for filename, facts in self.mlsd():
                if facts['type'] == 'file':
                    path = filename
                    size = facts['size']
                    timestamp = str_to_epoch(facts['modify'])
                    #print(path, size, timestamp)
                    file_list.append((path, size, timestamp))
        except:
            # If MLSD FTP command is not supported fallback to NLST command
            try:
                for filename in self.nlst():
                    # Check is name file or directory.
                    # If name is directory set to directory and return to previous
                    # If name is file check size and timestamp
                    try:
                        self.cwd(filename)
                        self.cwd('..')
                    except:
                        # is file
                        path = filename
                        
                        # Get file size with SIZE command
                        # if command is supported by FTP server.
                        # Otherwise set to 0.
                        if error_count_SIZE < MAX_ERROR_COUNT_SIZE:
                            try:
                                size = self.size(filename)
                            except:
                                size = 0
                                error_count_SIZE += 1
                        else:
                            size = 0
                        
                        # Get file timestamp with MDTM command
                        # if command is supported by FTP server.
                        # Otherwise set to localtime of FTP query.
                        if error_count_MDTM < MAX_ERROR_COUNT_MDTM:
                            try:
                                timestamp = str_to_timestamp(self.mdtm(filename), tz=dev_tz, format_code='%Y%m%d%H%M%S')
                            except:
                                timestamp = current_time
                                error_count_MDTM += 1
                        else:
                            timestamp = current_time
                        
                        file_list.append((path, size, timestamp))
            except:
                self.abort()
                raise ConnectionError
        finally:
            return file_list
