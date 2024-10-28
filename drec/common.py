import os
import copy
from datetime import datetime
from zoneinfo import ZoneInfo
import logging
import zipfile


def str_to_timestamp(dt_str, tz='UTC', format_code='%Y-%m-%d %H:%M:%S.%f'):
    """
    Convert date and time string to timestamp (UNIX epoch)
    
    Parameters
    ----------
    dt_str : str
        Date and time
    tz : str
        Timezone settings. Default UTC
    format_code : str
        Format code for strptime() method.
        Default %Y-%m-%d %H:%M:%S.%f (YYYY-MM-DD HH:MM:SS.SSSSSS)
    
    Returns
    -------
    timestamp : float
        Date and time in timestamp format (UNIX epoch)
    
    Notes
    -----
    List of tz database time zones
    https://en.wikipedia.org/wiki/List_of_tz_database_time_zones
    
    List of strftime() format codes
    https://docs.python.org/3/library/datetime.html#strftime-and-strptime-format-codes
    """
    
    # Set time zone
    timezone = ZoneInfo(tz)

    # Convert string to date and time with appropriate timezone
    dt = datetime.strptime(dt_str, format_code).replace(tzinfo=timezone)
    
    # Return timestamp
    return dt.timestamp()


def dt_to_str(dt, format_code='%Y-%m-%d %H:%M:%S.%f'):
    """
    Convert datetime to string
    
    Parameters
    ----------
    dt : datetime
        Date and time
    format_code : str
        Format code for strftime() method.
        Default %Y-%m-%d %H:%M:%S.%f (YYYY-MM-DD HH:MM:SS.SSSSSS)
    
    Returns
    -------
    datetime : str
        Date and time defined by format_code
    
    Note
    ----
    List of strftime() format codes
    https://docs.python.org/3/library/datetime.html#strftime-and-strptime-format-codes
    """
    
    return dt.strftime(format_code)


def timestamp_to_str(timestamp, tz='UTC', format_code='%Y-%m-%d %H:%M:%S.%f'):
    """
    Convert timestamp (UNIX epoch) to string
    
    Parameters
    ----------
    timestamp : float
        Timestamp in UNIX epoch format
    tz : str
        Timezone settings. Default UTC
    format_code : str
        Format code for strftime() method.
        Default %Y-%m-%d %H:%M:%S.%f (YYYY-MM-DD HH:MM:SS.SSSSSS)
    
    Returns
    -------
    datetime : str
        Date and time defined by format_code
    
    Notes
    -----
    List of tz database time zones
    https://en.wikipedia.org/wiki/List_of_tz_database_time_zones
    
    List of strftime() format codes
    https://docs.python.org/3/library/datetime.html#strftime-and-strptime-format-codes
    """
    
    # Set time zone
    timezone = ZoneInfo(tz)
    
    # Create date and time from timestamp and time zone
    dt = datetime.fromtimestamp(timestamp, timezone)
    
    # Return string defined by format_code
    return dt.strftime(format_code)


def filter_file_list(file_list, directory='COMTRADE', rem_hdr_zip=True):
    """
    Filter and sort file list based on filename:
        - Replace directory separators for GNU/Linux (replace '\\' with '/')
        - Sort files by filename
        - Remove empty COMTRADE directories
        - Remove files which are not disturbance records
        - Remove zipped HDR files (ABB IEDs)
    
    Parameters
    ----------
    file_list : list of tuples
        List of files (path, size, timestamp)
    directory : str
        Directory for disturbance records.
        Default COMTRADE
    rem_hdr_zip : bool
        Remove zipped HDR file from the list
    
    Returns
    -------
    filtered_file_list : list of tuples
        Sorted list of disturbance record files
    """
    
    # Replace directory separators for GNU/Linux (replace '\' with '/')
    # Sort the list by filename
    sorted_file_list = sorted([(path.replace('\\', '/'), size, time) for (path, size, time) in file_list])
    
    # Remove empty COMTRADE directories
    # Remove files which are not disturbance records
    # Note: Empty directory COMTRADE does not contain basename
    filtered_file_list = [f for f in sorted_file_list if directory in f[0] and os.path.basename(f[0])]
    
    # Remove zipped HDR files from the list (ABB IEDs)
    if rem_hdr_zip:
        for index in range(len(filtered_file_list)-1, -1, -1):
            # Note: It's necesary to search through items from the end of the list (in reverse order)
            #       because items are removed from the list which is being searched
            if filtered_file_list[index][0].lower().endswith('h.zip'):
                # Remove h from filename (fifth symbol from the back)
                search_zip = filtered_file_list[index][0][:-5] + filtered_file_list[index][0][-4:]
                for (file, size, time) in filtered_file_list:
                    if file == search_zip:
                        # If zipped disturbance record and zipped HDR file is found in the list
                        # remove zipped HDR file from the list
                        filtered_file_list.pop(index)
                        break
    
    return filtered_file_list


def order_file_list(sorted_file_list, criteria=('.cfg', '.cff', '.zip', '.dat', '.hdr', '.inf')):
    """
    Ordered directory file list based on filename and extension.
    Files with the same filename are ordered with given criteria.
    Note: input list must be sorted by filename
    
    Parameters
    ----------
    sorted_file_list : list of tuples
        Sorted list of files (path or filename, size, timestamp)
        Note: input list must be sorted by filename
        Note: size and timestamp are optional
    criteria : iterable
        Criteria for ordering files with the same filename. Files are ordered
        first by set extension criteria and than the rest of the files with the
        same filename.
        Default ('.cfg', '.cff', '.zip', '.dat', '.hdr', '.inf')
    
    Returns
    -------
    ordered_file_list : list of tuples
        Ordered list of disturbance record files
    """
    
    # Initialize
    ordered_file_list = []
    n = len(sorted_file_list)
    if n > 0:
        index_start = 0
        search_name = os.path.basename(os.path.splitext(sorted_file_list[0][0])[0])
    
    # Order list according to set criteria
    for index in range(n):
        # Next file in sorted dir list
        if index < n-1:
            next_file_name = os.path.basename(os.path.splitext(sorted_file_list[index+1][0])[0])
        else:
            next_file_name = os.path.basename(os.path.splitext(sorted_file_list[index][0])[0])
        
        # Compare search name with next file name or end of the list -> order files
        if search_name != next_file_name or index == n-1:
            # Set stop index
            index_stop = index + 1
            
            # Order files by extension criteria
            for ext in criteria:
                # Order files with required extension
                for f in sorted_file_list[index_start:index_stop]:
                    if os.path.splitext(f[0])[1].lower() == ext.lower():
                        ordered_file_list.append(f)
                        break
            else:
                # Remaining files (if they exist) with extension not set in criteria
                for f in sorted_file_list[index_start:index_stop]:
                    if os.path.splitext(f[0])[1].lower() not in criteria:
                        ordered_file_list.append(f)
            
            # Set start index and search_name for new search
            index_start = index_stop
            search_name = next_file_name
    
    return ordered_file_list


def group_file_list(ordered_file_list):
    """
    Group ordered directory file list based on filename
    
    Parameters
    ----------
    ordered_file_list : list of tuples
        Ordered list of files (path, size, timestamp)
        Note: size and timestamp are optional.
    
    Returns
    -------
    grouped_dir_list : list of list of tuples
        Grouped file list
    """
    
    # Initialize
    grouped_dir_list = []
    n = len(ordered_file_list)
    if n > 0:
        index_start = 0
        search_name = os.path.basename(os.path.splitext(ordered_file_list[0][0])[0])
    
    # Group list based or disturbance record filename
    for index in range(n):
        # Next file in ordered dir list
        if index < n-1:
            next_file_name = os.path.basename(os.path.splitext(ordered_file_list[index+1][0])[0])
        else:
            next_file_name = os.path.basename(os.path.splitext(ordered_file_list[index][0])[0])
        
        # Compare search name with next file name or end of the list -> group files
        if search_name != next_file_name or index == n-1:
            # Set stop index
            index_stop = index + 1
            
            # Append new group
            grouped_dir_list.append(ordered_file_list[index_start:index_stop])
                
            # Set start index and search_name for new search
            index_start = index_stop
            search_name = next_file_name
    
    return grouped_dir_list


def group_dev_file_list(file_list, directory='COMTRADE', criteria=('.cfg', '.cff', '.zip', '.dat', '.hdr', '.inf')):
    """
    Filter, sort, order and group file list based on filename and :
        - Replace directory separators for GNU/Linux (replace '\\' with '/')
        - Sort files by filename
        - Remove empty COMTRADE directories
        - Remove files which are not disturbance records
        - Remove zipped HDR files (ABB IEDs)
        - Order list by criteria
        - Group list by filename
    
    Note: method is combination of methods:
            - filter_file_list()
            - order_file_list()
            - group_file_list()
    
    Parameters
    ----------
    file_list : list of tuples
        List of files (path, size, timestamp)
    directory : str
        Device directory for disturbance records.
        Default COMTRADE
    criteria : iterable
        Criteria for ordering files with the same filename.
        Default ('.cfg', '.cff', '.zip', '.dat', '.hdr', '.inf')
    
    Returns
    -------
    grouped_file_list : list of list of tuples
        Grouped list of disturbance record files
    """
    
    return group_file_list(
             order_file_list(
               filter_file_list(file_list, directory), criteria))


def is_downloaded(dev_path, local_dir_path, dev_size=0, dev_timestamp=0, size=False, time=False):
    """
    Check is file downloaded from device.
    Local filename must end with device basename.
    Size and timestamp check are optional (disabled by default).
    
    Parameters
    ----------
    dev_path : str
        Device file path
    local_dir_path : str
        Path to local directory
    dev_size : int
        Device file size in bytes. Necessary only if size=True.
        Default 0
    dev_timestamp : float
        Device timestamp in seconds. Necessary only if time=True.
        Default 0
    size : bool
        Compare local and device file size.
        Note: File size on different operating systems or devices may differ.
        Default False
    time : bool
        Compare local and device file timestamp.
        Default False
    
    Returns
    -------
    downloaded : bool
        Return True if file is downloaded, else return False
    """
    
    # Check does local file exist
    dev_basename = os.path.basename(dev_path)
    local_path = ''
    for local_basename in os.listdir(local_dir_path):
        if local_basename.endswith(dev_basename):
            local_path = os.path.join(local_dir_path, local_basename)
            break
    
    # Check if path/basename is file
    if not os.path.isfile(local_path):
        return False

    # Compare device and local file size
    # Note: Siprotec 4 size is always 0
    if size and os.path.getsize(local_path) != dev_size:
        return False
    
    # Compare device and local timestamp
    #
    # Note: ABB 615 and 620 series do not return UTC timestamp when file was created. During summer time IED
    #       returns UTC timestamp but after switchover to winter time IED shows timestamp UTC + DST offset
    #       even for files created during summer time. When file directory is read timestamp depends on the
    #       current DST offset and changes depending on current winter/summer time offset:
    #       Timestamp = Current time - (timezone offset + current DST offset).
    # Note: GE C70 relays return time when file directory was read (not when file was created).

    if time and int(os.path.getmtime(local_path)) != int(dev_timestamp):
        return False
    
    # File is already downloaded. All checks are OK
    return True


def dir_list_diff(dev_dir_list, local_dir_path, dev_dir='COMTRADE'):
    """
    Difference between local and device file directory.
    Check: local file name must end with device basename.
    
    Parameters
    ----------
    dev_dir_list : list of tuples
        List of device files (path, size, timestamp)
    local_dir_path : str
        Path to local directory
    dev_dir : str
        Device directory for disturbance records. Default COMTRADE.
    
    Returns
    -------
    dir_list_diff : list
        List of file differences (full local path)
    """
    
    # Set of filtered device file list
    dev_files   = {os.path.basename(path) for path, size, timestamp in filter_file_list(dev_dir_list, dev_dir)}
    
    # Set of Local files (exclude directories)
    local_files = {filename for filename in os.listdir(local_dir_path) if os.path.isfile(os.path.join(local_dir_path, filename))}
    
    # Set of matches between local and device files 
    match_files = {local_file for local_file in local_files for dev_file in dev_files if local_file.endswith(dev_file)}
    
    # Difference between local and device files
    return [os.path.join(local_dir_path, filename) for filename in sorted(local_files - match_files)]


def get_trigger_time(path, logger=None, tz='UTC'):
    """
    Get trigger time from Comtrade file.
    In case od invalid Comtrade file use file creation date and time.
    
    Parameters
    ----------
    path : str
        Path to comtrade cfg, cff or zip (which contains cfg or cff) file
    logger :
        Logger
    tz : str
        Local time zone settings (pytz). Used only in case it's not possible to read
        trigger time stamp from comtrade file. Default UTC
    
    Returns
    -------
    trigger_time : str
        Date and time in format YYYYMMDD_HHMMSS
    
    Note
    ----
    List of tz database time zones
    https://en.wikipedia.org/wiki/List_of_tz_database_time_zones
    """
    
    ext = os.path.splitext(path)[1].lower()
    
    try:
        if ext in ('.cfg', '.cff'):
            # Read config file line by line and return trigger time
            with open(path, 'r', encoding='utf-8', newline='\r\n') as f:
                # Search for CFG file separator in CFF file
                if ext == '.cff':
                    for line in f:
                        if line.strip() == '--- file type: CFG ---':
                            break
                
                # Read first line - station_name, rec_rev_id, rev_year
                f.readline()
                
                # Read second line - number of channels, analog channels, digital channels
                temp_list = f.readline().split(',')
                TT = int(temp_list[0])
                
                # Read analog and digital channels
                for ch in range(TT):
                    f.readline()
                
                # Read sampling frequency
                f.readline()
                
                # Read number of sampling rates
                nrates = int(f.readline()) 
                if nrates == 0:
                    nrates = 1
                
                # Read sampling rates
                for index in range(nrates):
                    f.readline()
                
                # Read first sample date and time
                f.readline()
                
                # Read trigger date and time
                trigger = f.readline().strip()
        
        elif ext == '.zip':
            # Open zip file
            # List files within zip file
            # Search for .cfg or .cff file
            # Read config file line by line and return trigger time
            with zipfile.ZipFile(path) as comtrade_zip:
                for zip_file in comtrade_zip.namelist():
                    zip_ext = os.path.splitext(zip_file)[1].lower()
                    if zip_ext in ('.cfg', '.cff'):
                        with comtrade_zip.open(zip_file) as f:
                            # Search for CFG file separator in CFF file
                            if zip_ext == '.cff':
                                for line in f:
                                    if line.decode('utf-8').strip() == '--- file type: CFG ---':
                                        break
                            
                            # Read first line - station_name, rec_rev_id, rev_year
                            f.readline()
                            
                            # Read second line - number of channels, analog channels, digital channels
                            temp_list = f.readline().decode('utf-8').split(',')
                            TT = int(temp_list[0])
                            
                            # Read analog and digital channels
                            for ch in range(TT):
                                f.readline()
                            
                            # Read sampling frequency
                            f.readline()
                            
                            # Read number of sampling rates
                            nrates = int(f.readline().decode('utf-8')) 
                            if nrates == 0:
                                nrates = 1
                            
                            # Read sampling rates
                            for index in range(nrates):
                                f.readline()
                            
                            # Read first sample date and time
                            f.readline()
                            
                            # Read trigger date and time
                            trigger = f.readline().decode('utf-8').strip()
                            
                        # Break loop
                        break
        
        if ext in ('.cfg', '.cff', '.zip'):
            # Extract date and time
            date, time = trigger.split(',')
            
            # Date
            temp_date = date.split('/')
            
            if len(temp_date[2]) <= 2:
                # Comtrade standard 1991
                month = int(temp_date[0])
                day   = int(temp_date[1])
                year  = int(temp_date[2])
                if year >= 70:
                    year += 1900
                else:
                    year += 2000
            else:
                # Comtrade format >1991
                day   = int(temp_date[0])
                month = int(temp_date[1])
                year  = int(temp_date[2])
            
            # Time
            temp_time = time.split(':')
            hour   = int(temp_time[0])
            minute = int(temp_time[1])
            second = round(float(temp_time[2]))
            
            trigger_time = '{:04d}{:02d}{:02d}_{:02d}{:02d}{:02d}'.format(year, month, day, hour, minute, second)
    except:
        if not logger:
            logger = logging.getLogger('drec')
        logger.warning('Error reading disturbance record trigger timestamp')
        trigger_time = timestamp_to_str(os.path.getmtime(path), tz, format_code='%Y%m%d_%H%M%S')
    
    return trigger_time


def file_attr_format_str_len(file_list):
    """
    Calculate max string width and return string format for file attributes
    name, size and timestamp
    
    Parameters
    ----------
    file_list : iterable
        File list with atributes (name, size, timestamp)
    
    Returns
    -------
    format_str_len : tuple
        Length of formated string
    """
    
    # Tab width and number of file atributes
    TAB_WIDTH = 8
    NO_ATTR = 3
    
    # Set initial max attribute string length to tab widtg
    max_str_len = [TAB_WIDTH-1] * NO_ATTR
    
    # Search for attribute max string length
    for f in file_list:
        for i in range(NO_ATTR):
            if i == 0:
                str_len = len(f[i])
            elif i == 1:
                str_len = len('%d' % f[i])
            else:
                str_len = len('%.3f' % f[i])
            if str_len > max_str_len[i]:
                max_str_len[i] = str_len
    
    # Set attribute string length as multiple of tab width
    str_len = [1] * NO_ATTR
    for i in range(NO_ATTR):
        str_len[i] = (max_str_len[i] // TAB_WIDTH + 1) * TAB_WIDTH
        if max_str_len[i] % TAB_WIDTH > TAB_WIDTH - 1:
            str_len[i] += TAB_WIDTH
            print(str_len[i])
    
    return tuple(str_len)
