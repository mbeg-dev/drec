import os
import yaml
import logging
import logging.handlers
import cerberus
import re

# IEC61850 library
from .iec61850 import iec61850

# FTP library
from .ftp import ftp


# Set logger
logger = logging.getLogger('drec')


def validate_config_schema(config, schema):
    """
    Validate config file yaml schema
    
    Parameters
    ----------
    config_file : dict
        Configuration file
    
    Returns
    -------
    valid : bool
        True if validation succeeds, otherwise False
    """
    
    # Create custom cerberus extension
    class CustomValidator(cerberus.Validator):
        def _validate_dependencies_protocol(self, constraint, field, value):
            """
            Check protocol parameter dependency

            The rule's arguments are validated against this schema:
            {'type': 'list'}
            """
            
            protocol = None
            if 'protocol' in self.document.keys():
                protocol = self.document['protocol']
            elif 'protocol' in self.root_document['GENERAL'].keys():
                protocol = self.root_document['GENERAL']['protocol']
            else:
                protocol = None
                self._error(field, "Protocol dependency error")
                return
            
            if protocol not in constraint:
                self._error(field, "Protocol dependency error")
        
        def _validate_dependencies_path(self, constraint, field, value):
            """
            Check dir_path dependencies
            
            The rule's arguments are validated against this schema:
            {'type': 'boolean'}
            """
            
            tags = (('name',     '<NAME>'),
                    ('bay',      '<BAY>'),
                    ('location', '<LOCATION>'),
                    ('device',   '<DEVICE>'),
                    ('comment',  '<COMMENT>'))
            
            if constraint is True:
                for param, tag in tags:
                    if tag in self.root_document['GENERAL']['dir_path'] and param not in self.document.keys():
                        self._error(param, "Part of dir_path")
        
        def _validate_supported_tags(self, constraint, field, value):
            """
            Check supported tags
            
            Searches for tags in string and validates against list of
            supported tags.
            
            The rule's arguments are validated against this schema:
            {'type': 'list'}
            """
            
            for tag in re.findall(r'<>|<[^>]+>', value):
                if tag not in constraint:
                    self._error(field, f'{tag} is not supported tag')


    # Initialize schema
    v = CustomValidator(schema)
    
    # Validate
    valid = v.validate(config, schema)
    
    # Print error message if validation is unsuccessful
    if not valid:
        logger.critical('Config file schema is not valid')
        logger.debug(v.errors)
    
    return valid


def read_config(file_path):
    """
    Read configuration file
    
    Parameters
    ----------
    file_path : str
        path to config file
    
    Returns
    -------
    config : dict
        list of config file parameters per substation
    """
    
    with open(file_path) as config_file:
        return yaml.safe_load(config_file)


def gen_path(data, path_tags, index):
    """
    Generate path from supported tags
    
    Parameters
    ----------
    data : dict
        Configuration file data
    path_tags : str
        Path with tags
    
    Returns
    -------
    path : str
        Path where supported tags are substituted with set names/parameters
    """
    
    path = path_tags
    
    if '<ROOT_PATH>' in path:
        path = path.replace('<ROOT_PATH>', data['GENERAL']['root_path'])
    
    if '<SUBSTATION>' in path:
        path = path.replace('<SUBSTATION>', data['GENERAL']['substation'])
    
    if '<NAME>' in path:
        path = path.replace('<NAME>', data['DEVICE'][index]['name'])
    
    if '<BAY>' in path:
        path = path.replace('<BAY>', data['DEVICE'][index]['bay'])
    
    if '<LOCATION>' in path:
        path = path.replace('<LOCATION>', data['DEVICE'][index]['location'])
    
    if '<DEVICE>' in path:
        path = path.replace('<DEVICE>', data['DEVICE'][index]['device'])
    
    if '<COMMENT>' in path:
        path = path.replace('<COMMENT>', data['DEVICE'][index]['comment'])
    
    return path


def gen_dir_path(data, index):
    """
    Generate disturbance record storage dir path from config file
    
    Parameters
    ----------
    data : dict
        config file data
    
    Returns
    -------
    dir_path : str
        Disturbance record storage path
    """
    
    return gen_path(data, data['GENERAL']['dir_path'], index)


def gen_log_path(data):
    """
    Generate disturbance record storage dir path from config file
    
    Parameters
    ----------
    data : dict
        config file data
    
    Returns
    -------
    log_path : str
        Log file path
    """
    
    return gen_path(data, data['GENERAL']['log_path'], None)


def valid_args(args, valid_args):
    """
    Generate dictionary only with valid arguments
    
    Parameters
    ----------
    args : dictionary
        All method arguments
    valid_args : dictionary
        All valid method arguments
    
    Returns
    -------
    valid_args : dictionary
        Only valid method arguments
    """
    
    return {key: val for key, val in args.items() if key in valid_args}


# Main loop
def client(config, sleep_timer, interrupt):
    """
    Client method
    
    Parameters
    ----------
    config : iterable
        Configuration file or files
    sleep_timer : int
        Delay in seconds between processing config files
    interrupt : threading.Event.Event() object
        Event() object from threading.Event library used to gracefully
        terminate program
    """
    
    # Loop through config files
    for config_count, config_file in enumerate(config):
        # Read config file
        data = read_config(config_file)
        
        # Log dirname
        logger_dirname = os.path.dirname(gen_log_path(data))
        
        # Create local download directiory if it doesn't exist
        if not os.path.isdir(logger_dirname):
            os.makedirs(logger_dirname)
        
        # Creating logger time rotating file handler
        trf_handler = logging.handlers.TimedRotatingFileHandler(gen_log_path(data), 
                                                                when='midnight',
                                                                backupCount=30)
        trf_handler.setLevel(logging.INFO)
        trf_format = logging.Formatter('%(asctime)s - %(name)-13s - %(levelname)-8s - %(message)s')
        trf_handler.setFormatter(trf_format)
        logger.addHandler(trf_handler)
        
        # Create list of general function call arguments
        valid_arg_list = (
            'protocol',
            'dev_port',
            'dev_dir',
            'user',
            'password',
            'con_timeout',
            'req_timeout',
            'poll_timeout',
            'ret_timeout',
            'no_retry',
            'dev_tz',
            'local_tz'
        )
        general_args = valid_args(data['GENERAL'], valid_arg_list)
        
        # Loop through devices
        for index, device in enumerate(data['DEVICE']):
            # Disturbance record local storage dirname
            local_dirname = gen_dir_path(data, index)
            
            # Create local download directiory if it doesn't exist
            if not os.path.isdir(local_dirname):
                os.makedirs(local_dirname)
            
            logger.debug('Download path: %s', local_dirname)
            
            # Create list of function call arguments
            # Device specific arguments take precedence over general arguments
            args = general_args.copy()
            args['local_dirname'] = local_dirname
            for key in device.keys():
                args[key] = device[key]
            
            # Download disturbance records via IEC61850
            if args['protocol'] == 'IEC61850':
                valid_arg_list = (
                    'dev_address',
                    'local_dirname',
                    'dev_dir',
                    'dev_port',
                    'req_timeout',
                    'poll_timeout',
                    'ret_timeout',
                    'no_retry',
                    'local_tz'
                )
                args = valid_args(args, valid_arg_list)
                drec = iec61850.IEC61850(interrupt)
                drec.download(**args)

                # Destroy iec61850 instance
                drec.destroy()
            
            # Download disturbance records via FTP
            elif args['protocol'] == 'FTP':
                valid_arg_list = (
                    'dev_address',
                    'local_dirname',
                    'dev_dir',
                    'dev_port',
                    'user',
                    'password',
                    'con_timeout',
                    'poll_timeout',
                    'ret_timeout'
                    'no_retry',
                    'dev_tz',
                    'local_tz'
                )
                args = valid_args(args, valid_arg_list)
                drec = ftp.FTPClient(interrupt)
                drec.download(**args)
            
            # Check interrupt flag and exit if necesary
            if interrupt.is_set(): break
        
        # Check interrupt flag and log exit message
        if interrupt.is_set():
            logger.info('Exited gracefully after interrupt')
        
        # Remove logger time rotating file handler
        logger.removeHandler(trf_handler)
        
        # Delay between reading/processing CONFIG files
        if 0 <= config_count < len(config)-1:
            if sleep_timer > 0:
                logger.debug('Timeout between reading/processing CONFIG files: {} s'.format(sleep_timer))
            interrupt.wait(sleep_timer)
        
        # Check interrupt flag and break loop
        if interrupt.is_set():
            break
