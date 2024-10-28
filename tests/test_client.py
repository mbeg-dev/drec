#!/usr/bin/env python3

###############################################################################
# client test file
###############################################################################

import pytest
from contextlib import nullcontext as does_not_raise

import copy
import os

from drec import client
from config.schema import schema

# Configuration IEC 61850
config_iec61850 = {
    'GENERAL': {
        'substation':   'Substation',
        'root_path':    '/test_path',
        'dir_path':     '<ROOT_PATH>/download/<SUBSTATION>/<BAY>_<NAME>/<COMMENT>',
        'log_path':     '<ROOT_PATH>/log/<SUBSTATION>.log',
        'protocol':     'IEC61850',
        'dev_port':     102,
        'dev_dir':      'COMTRADE',
        'req_timeout':  5,
        'poll_timeout': 0,
        'no_retry':     1,
        'ret_timeout':  10,
        'local_tz':     'Europe/Zagreb'
    },
    'DEVICE': [
        {
        'dev_address':  '192.168.0.1',
        'name':         'Feeder_1',
        'bay':          'J01',
        'location':     'S1',
        'device':       'F301',
        'comment':      'Feeder_terminal_1'
        },
        {
        'dev_address':  '192.168.0.2',
        'name':         'Feeder_2',
        'bay':          'J02',
        'location':     'S1',
        'device':       'F301',
        'comment':      'Feeder_terminal_2'
        }
    ]
}

# Configuration FTP
config_ftp = {
    'GENERAL': {
        'substation':   'Substation',
        'root_path':    '/test_path',
        'dir_path':     '<ROOT_PATH>/download/<SUBSTATION>/<BAY>_<NAME>/<COMMENT>',
        'log_path':     '<ROOT_PATH>/log/<SUBSTATION>.log',
        'protocol':     'FTP',
        'dev_port':     21,
        'dev_dir':      'COMTRADE',
        'user':         'user',
        'password':     'password',
        'con_timeout':  60,
        'poll_timeout': 0,
        'ret_timeout':  10,
        'no_retry':     1,
        'dev_tz':       "UTC",
        'local_tz':     'Europe/Zagreb'
    },
    'DEVICE': [
        {
        'dev_address':  '192.168.0.1',
        'name':         'Feeder_1',
        'bay':          'J01',
        'location':     'S1',
        'device':       'F301',
        'comment':      'Feeder_terminal_1'
        },
        {
        'dev_address':  '192.168.0.2',
        'name':         'Feeder_2',
        'bay':          'J02',
        'location':     'S1',
        'device':       'F301',
        'comment':      'Feeder_terminal_2'
        }
    ]
}

def test_validate_config_schema():
    # Assert config files
    assert client.validate_config_schema(config_iec61850, schema)
    assert client.validate_config_schema(config_ftp, schema)
    
    # Check custom validation validate_dependencies_protocol
    config = copy.deepcopy(config_iec61850)
    del config['GENERAL']['protocol']
    assert not client.validate_config_schema(config, schema)
    
    config = copy.deepcopy(config_iec61850)
    del config['GENERAL']['protocol']
    config['DEVICE'][0]['protocol'] = 'IEC61850'
    assert not client.validate_config_schema(config, schema)
    
    config = copy.deepcopy(config_iec61850)
    del config['GENERAL']['protocol']
    config['DEVICE'][1]['protocol'] = 'IEC61850'
    assert not client.validate_config_schema(config, schema)
    
    config = copy.deepcopy(config_iec61850)
    del config['GENERAL']['protocol']
    config['DEVICE'][0]['protocol'] = 'IEC61850'
    config['DEVICE'][1]['protocol'] = 'IEC61850'
    assert client.validate_config_schema(config, schema)
    
    # Check custom validation validate_dependencies_path
    config = copy.deepcopy(config_iec61850)
    del config['DEVICE'][0]['bay']
    assert not client.validate_config_schema(config, schema)
    
    config = copy.deepcopy(config_iec61850)
    del config['DEVICE'][1]['name']
    assert not client.validate_config_schema(config, schema)
    
    config = copy.deepcopy(config_iec61850)
    del config['DEVICE'][1]['comment']
    assert not client.validate_config_schema(config, schema)
    
    # Check custom validation validate_supported_tags
    config = copy.deepcopy(config_iec61850)
    config['GENERAL']['dir_path'] = '<ROOT_PATH>/download/<TEST>/<SUBSTATION>/<BAY> - <NAME>/<COMMENT>'
    assert not client.validate_config_schema(config, schema)
    
    config = copy.deepcopy(config_iec61850)
    config['GENERAL']['log_path'] = '<ROOT_PATH>/log/<SUBSTATION><TEST>.log'
    assert not client.validate_config_schema(config, schema)


def test_read_config():
    path = 'tests/conf_test_cases/conf_IEC61850.yaml'
    config = client.read_config(path)
    assert config == config_iec61850
    
    path = 'tests/conf_test_cases/conf_FTP.yaml'
    config = client.read_config(path)
    assert config == config_ftp


def test_gen_path():
    config = copy.deepcopy(config_iec61850)
    config['GENERAL']['dir_path'] = '<ROOT_PATH>/<SUBSTATION>/<BAY> - <NAME>/=<BAY>+<LOCATION>-<DEVICE> - <COMMENT>'
    config['GENERAL']['log_path'] = '<ROOT_PATH>/<SUBSTATION>/log'
    
    index = 0
    generated_path = config['GENERAL']['root_path'] \
                   + '/' \
                   + config['GENERAL']['substation'] \
                   + '/' \
                   + config['DEVICE'][index]['bay'] \
                   + ' - ' \
                   + config['DEVICE'][index]['name'] \
                   + '/=' \
                   + config['DEVICE'][index]['bay'] \
                   + '+' \
                   + config['DEVICE'][index]['location'] \
                   + '-' \
                   + config['DEVICE'][index]['device'] \
                   + ' - ' \
                   + config['DEVICE'][index]['comment']
    
    assert client.gen_path(config, config['GENERAL']['dir_path'], index) == generated_path
    assert client.gen_dir_path(config, index) == generated_path
    
    index = 1
    generated_path = config['GENERAL']['root_path'] \
                   + '/' \
                   + config['GENERAL']['substation'] \
                   + '/' \
                   + config['DEVICE'][index]['bay'] \
                   + ' - ' \
                   + config['DEVICE'][index]['name'] \
                   + '/=' \
                   + config['DEVICE'][index]['bay'] \
                   + '+' \
                   + config['DEVICE'][index]['location'] \
                   + '-' \
                   + config['DEVICE'][index]['device'] \
                   + ' - ' \
                   + config['DEVICE'][index]['comment']
    
    assert client.gen_path(config, config['GENERAL']['dir_path'], index) == generated_path
    assert client.gen_dir_path(config, index) == generated_path
    
    generated_path = config['GENERAL']['root_path'] \
                   + '/' \
                   + config['GENERAL']['substation'] \
                   + '/log'
    
    assert client.gen_log_path(config) == generated_path


def test_valid_args():
    config = {
        'key1': 1,
        'key2': 2,
        'key3': 3,
        'key4': 4,
        'key5': 5,
        'key6': 6
    }
    
    valid_keys = ('key1', 'key3', 'key6')
    
    valid_config = {
        'key1': 1,
        'key3': 3,
        'key6': 6
    }
    
    assert client.valid_args(config, valid_keys) == valid_config
