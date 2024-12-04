import os
import shutil
import logging
import traceback

# Import libiec61850
from .libiec61850 import iec61850

# Import from common
from ..common import is_downloaded
from ..common import group_dev_file_list
from ..common import get_trigger_time
from ..common import dir_list_diff
from ..common import file_attr_format_str_len


# Set logger name to module name
logger = logging.getLogger('drec.iec61850')


class IEC61850(iec61850.IEC61850_client):
    """
    Class for disturbance record download via IEC 61850
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
    
    
    def download(self, dev_address, local_dirname, dev_dir='COMTRADE', dev_port=102, req_timeout=5, poll_timeout=0, ret_timeout=10, no_retry=1, local_tz='UTC'):
        """
        Download disturbance records
        
        Parameters
        ----------
        dev_address : str
            IED IP address or hostname
        local_dirname : str
            Path to local storage directory
        dev_dir : str
            IED directory for disturbance records. Default is COMTRADE
        dev_port : int
            IED port. Default is 102
        req_timeout : int
            Request timeout in miliseconds. libIEC61850 internally uses
            request timeout parameter as 32-bit unsigned int in miliseconds.
            Default is 5 s
        poll_timeout : int
            Timeout between polling requests in seconds. Default is 0 s
        ret_timeout : int
            Retry timeout in seconds. Default is 10 s
        no_retry : int
            Number of retries after error. Default 1
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
                    self.connect(dev_address, dev_port)
                    logger.debug('Connected to %s:%s', dev_address, dev_port)
                
                # Check interrupt flag and exit if necesary
                if self._interrupt.is_set(): break
                
                # Download file directory
                dev_file_list = self.get_file_directory('')
                
                # Convert timestamp from ms to s
                dev_file_list = tuple(((name, size, time/1000) for name, size, time in dev_file_list))
                
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
                for dist_rec in group_dev_file_list(dev_file_list, dev_dir):
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
                            
                            # Request timeout in miliseconds
                            self.set_request_timeout(req_timeout * 1000)
                            
                            # Check interrupt flag and exit if necesary
                            #if self._interrupt.is_set(): break
                            
                            # Download disturbance record
                            logger.debug('Started downloading: %s %s', dev_address, dev_path)
                            self.get_file(dev_path, local_path)
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
                
                # Compare list of local files with list of ied disturbance record files and search for differences
                # Move local disturbance records which do not exist in IED anymore to archive directory
                archive_path = os.path.join(local_dirname, 'archive')
                for f in dir_list_diff(dev_file_list, local_dirname, dev_dir):
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
                    try:
                        self.abort()
                    except ConnectionError:
                        # If the connection is not in "connected" state an
                        # ConnectionError exception NOT CONNECTED will be raised
                        pass
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
            self.abort()
        except ConnectionError:
            # If the connection is not in "connected" state as
            # ConnectionError exception NOT CONNECTED will be raised
            pass
        logger.debug('Disconnected from %s:%s', dev_address, dev_port)
