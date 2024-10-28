#!/usr/bin/env python3

###############################################################################
# drec/common test file
###############################################################################

import pytest
from contextlib import nullcontext as does_not_raise

from drec import common

import os
from datetime import datetime
from zoneinfo import ZoneInfo


LOCAL_DR_PATH = 'tests/DR_test_cases'


def test_str_to_timestamp():
    format_code='%Y-%m-%d %H:%M:%S.%f'
    date_time_str = '2000-01-01 00:00:00.000000'
    epoch_UTC = 946684800.000000
    epoch_CET = 946681200.000000
    
    assert common.str_to_timestamp(date_time_str, tz='UTC', format_code=format_code) == epoch_UTC
    assert common.str_to_timestamp(date_time_str, tz='CET', format_code=format_code) == epoch_CET


def test_dt_to_str():
    format_code='%Y-%m-%d %H:%M:%S.%f'
    date_time_str = '2000-01-01 00:00:00.000000'
    date_time_UTC = datetime.strptime(date_time_str, format_code).replace(tzinfo=ZoneInfo('UTC'))
    date_time_CET = datetime.strptime(date_time_str, format_code).replace(tzinfo=ZoneInfo('CET'))
    
    assert common.dt_to_str(date_time_UTC, format_code=format_code) == date_time_str
    assert common.dt_to_str(date_time_CET, format_code=format_code) == date_time_str


def test_timestamp_to_str():
    format_code='%Y-%m-%d %H:%M:%S.%f'
    date_time_str = '2000-01-01 00:00:00.000000'
    epoch_UTC = 946684800.000000
    epoch_CET = 946681200.000000
    
    assert common.timestamp_to_str(epoch_UTC, tz='UTC', format_code=format_code) == date_time_str
    assert common.timestamp_to_str(epoch_CET, tz='CET', format_code=format_code) == date_time_str


def test_filter_file_list():
    files =          [('file_1.txt', 0, 0),
                      ('file_2_txt', 0, 0),
                      ('COMTRADE/file_1.txt', 0, 0),
                      ('COMTRADE\\file_3.txt', 0, 0),
                      ('COMTRADE\\', 0, 0),
                      ('COMTRADE/file_2h.zip', 0, 0),
                      ('COMTRADE/file_4.zip', 0, 0),
                      ('COMTRADE/file_2.zip', 0, 0)]
    
    filtered_files = [('COMTRADE/file_1.txt', 0, 0),
                      ('COMTRADE/file_2.zip', 0, 0),
                      ('COMTRADE/file_3.txt', 0, 0),
                      ('COMTRADE/file_4.zip', 0, 0)]
    
    assert common.filter_file_list(files) == filtered_files
    assert common.filter_file_list(files, directory='COMTRADE') == filtered_files


def test_order_file_list():
    filtered_files = [('COMTRADE/file_1.txt', 0, 0),
                      ('COMTRADE/file_2.zip', 0, 0),
                      ('COMTRADE/file_3.txt', 0, 0),
                      ('COMTRADE/file_3.zip', 0, 0),
                      ('COMTRADE/file_4.cfg', 0, 0),
                      ('COMTRADE/file_4.dat', 0 ,0),
                      ('COMTRADE/file_4.hdr', 0, 0),
                      ('COMTRADE/file_5.inf', 0, 0),
                      ('COMTRADE/file_6.txt', 0, 0),
                      ('COMTRADE/file_7.txt', 0, 0),
                      ('COMTRADE/file_7.hdr', 0, 0),
                      ('COMTRADE/file_7.inf', 0 ,0),
                      ('COMTRADE/file_7.dat', 0, 0),
                      ('COMTRADE/file_7.cfg', 0, 0),
                      ('COMTRADE/file_7.zip', 0, 0),
                      ('COMTRADE/file_7.cff', 0, 0)]
    
    ordered_files  = [('COMTRADE/file_1.txt', 0, 0),
                      ('COMTRADE/file_2.zip', 0, 0),
                      ('COMTRADE/file_3.zip', 0, 0),
                      ('COMTRADE/file_3.txt', 0, 0),
                      ('COMTRADE/file_4.cfg', 0, 0),
                      ('COMTRADE/file_4.dat', 0 ,0),
                      ('COMTRADE/file_4.hdr', 0, 0),
                      ('COMTRADE/file_5.inf', 0, 0),
                      ('COMTRADE/file_6.txt', 0, 0),
                      ('COMTRADE/file_7.cfg', 0, 0),
                      ('COMTRADE/file_7.cff', 0, 0),
                      ('COMTRADE/file_7.zip', 0 ,0),
                      ('COMTRADE/file_7.dat', 0, 0),
                      ('COMTRADE/file_7.hdr', 0, 0),
                      ('COMTRADE/file_7.inf', 0, 0),
                      ('COMTRADE/file_7.txt', 0, 0)]
    
    assert common.order_file_list(filtered_files) == ordered_files
    assert common.order_file_list(filtered_files, criteria=('.cfg', '.cff', '.zip', '.dat', '.hdr', '.inf')) == ordered_files
    
    
    filtered_files = [('COMTRADE/file_1.txt', 0, 0),
                      ('COMTRADE/file_2.zip', 0, 0),
                      ('COMTRADE/file_3.txt', 0, 0),
                      ('COMTRADE/file_3.zip', 0, 0),
                      ('COMTRADE/file_4.cfg', 0, 0),
                      ('COMTRADE/file_4.dat', 0 ,0),
                      ('COMTRADE/file_4.hdr', 0, 0),
                      ('COMTRADE/file_5.inf', 0, 0),
                      ('COMTRADE/file_6.txt', 0, 0),
                      ('COMTRADE/file_7.txt', 0, 0),
                      ('COMTRADE/file_7.hdr', 0, 0),
                      ('COMTRADE/file_7.inf', 0 ,0),
                      ('COMTRADE/file_7.dat', 0, 0),
                      ('COMTRADE/file_7.cfg', 0, 0),
                      ('COMTRADE/file_7.zip', 0, 0),
                      ('COMTRADE/file_7.cff', 0, 0)]
    
    ordered_files  = [('COMTRADE/file_1.txt', 0, 0),
                      ('COMTRADE/file_2.zip', 0, 0),
                      ('COMTRADE/file_3.zip', 0, 0),
                      ('COMTRADE/file_3.txt', 0, 0),
                      ('COMTRADE/file_4.hdr', 0, 0),
                      ('COMTRADE/file_4.cfg', 0, 0),
                      ('COMTRADE/file_4.dat', 0 ,0),
                      ('COMTRADE/file_5.inf', 0, 0),
                      ('COMTRADE/file_6.txt', 0, 0),
                      ('COMTRADE/file_7.hdr', 0, 0),
                      ('COMTRADE/file_7.cfg', 0, 0),
                      ('COMTRADE/file_7.inf', 0, 0),
                      ('COMTRADE/file_7.cff', 0, 0),
                      ('COMTRADE/file_7.zip', 0 ,0),
                      ('COMTRADE/file_7.dat', 0, 0),
                      ('COMTRADE/file_7.txt', 0, 0)]
    
    assert common.order_file_list(filtered_files, criteria=('.hdr', '.cfg', '.inf', '.cff', '.zip', '.dat')) == ordered_files


def test_group_file_list():
    ordered_files  = [('COMTRADE/file_1.txt', 0, 0),
                      ('COMTRADE/file_2.zip', 0, 0),
                      ('COMTRADE/file_3.zip', 0, 0),
                      ('COMTRADE/file_3.txt', 0, 0),
                      ('COMTRADE/file_4.cfg', 0, 0),
                      ('COMTRADE/file_4.dat', 0 ,0),
                      ('COMTRADE/file_4.hdr', 0, 0),
                      ('COMTRADE/file_5.inf', 0, 0),
                      ('COMTRADE/file_6.txt', 0, 0),
                      ('COMTRADE/file_7.cfg', 0, 0),
                      ('COMTRADE/file_7.cff', 0, 0),
                      ('COMTRADE/file_7.zip', 0 ,0),
                      ('COMTRADE/file_7.dat', 0, 0),
                      ('COMTRADE/file_7.hdr', 0, 0),
                      ('COMTRADE/file_7.inf', 0, 0),
                      ('COMTRADE/file_7.txt', 0, 0)]
    
    grouped_files = [[('COMTRADE/file_1.txt', 0, 0)],
                     [('COMTRADE/file_2.zip', 0, 0)],
                     [('COMTRADE/file_3.zip', 0, 0),
                      ('COMTRADE/file_3.txt', 0, 0)],
                     [('COMTRADE/file_4.cfg', 0, 0),
                      ('COMTRADE/file_4.dat', 0 ,0),
                      ('COMTRADE/file_4.hdr', 0, 0)],
                     [('COMTRADE/file_5.inf', 0, 0)],
                     [('COMTRADE/file_6.txt', 0, 0)],
                     [('COMTRADE/file_7.cfg', 0, 0),
                      ('COMTRADE/file_7.cff', 0, 0),
                      ('COMTRADE/file_7.zip', 0 ,0),
                      ('COMTRADE/file_7.dat', 0, 0),
                      ('COMTRADE/file_7.hdr', 0, 0),
                      ('COMTRADE/file_7.inf', 0, 0),
                      ('COMTRADE/file_7.txt', 0, 0)]]
    
    assert common.group_file_list(ordered_files) == grouped_files


def test_group_dev_file_list():
    files          = [('COMTRADE/file_7.txt', 0, 0),
                      ('COMTRADE/file_1.txt', 0, 0),
                      ('COMTRADE/file_3.zip', 0, 0),
                      ('COMTRADE/file_4.cfg', 0, 0),
                      ('COMTRADE/file_4.dat', 0 ,0),
                      ('COMTRADE/file_4.hdr', 0, 0),
                      ('COMTRADE/file_6.txt', 0, 0),
                      ('COMTRADE/file_7.hdr', 0, 0),
                      ('COMTRADE/file_7.inf', 0 ,0),
                      ('COMTRADE/file_3.txt', 0, 0),
                      ('COMTRADE/file_7.dat', 0, 0),
                      ('COMTRADE/file_2.zip', 0, 0),
                      ('COMTRADE/file_7.cfg', 0, 0),
                      ('COMTRADE/file_5.inf', 0, 0),
                      ('COMTRADE/file_7.zip', 0, 0),
                      ('COMTRADE/file_7.cff', 0, 0)]
    
    grouped_files = [[('COMTRADE/file_1.txt', 0, 0)],
                     [('COMTRADE/file_2.zip', 0, 0)],
                     [('COMTRADE/file_3.zip', 0, 0),
                      ('COMTRADE/file_3.txt', 0, 0)],
                     [('COMTRADE/file_4.cfg', 0, 0),
                      ('COMTRADE/file_4.dat', 0 ,0),
                      ('COMTRADE/file_4.hdr', 0, 0)],
                     [('COMTRADE/file_5.inf', 0, 0)],
                     [('COMTRADE/file_6.txt', 0, 0)],
                     [('COMTRADE/file_7.cfg', 0, 0),
                      ('COMTRADE/file_7.cff', 0, 0),
                      ('COMTRADE/file_7.zip', 0 ,0),
                      ('COMTRADE/file_7.dat', 0, 0),
                      ('COMTRADE/file_7.hdr', 0, 0),
                      ('COMTRADE/file_7.inf', 0, 0),
                      ('COMTRADE/file_7.txt', 0, 0)]]
    
    assert common.group_dev_file_list(files) == grouped_files
    assert common.group_dev_file_list(files, directory='COMTRADE', criteria=('.cfg', '.cff', '.zip', '.dat', '.hdr', '.inf')) == grouped_files


def test_is_downloaded():
    assert common.is_downloaded('COMTRADE/test_1991.cfg', LOCAL_DR_PATH)
    
    assert common.is_downloaded('COMTRADE/test_1991.cfg', LOCAL_DR_PATH, dev_size=630, size=True)


def test_dir_list_diff():
    files =      [('COMTRADE/test_1991.cfg', 0, 0),
                  ('COMTRADE/test_1998.cfg', 0, 0),
                  ('COMTRADE/test_2013.cff', 0, 0),
                  ('COMTRADE/test_2013.cfg', 0, 0)]
    
    files_diff = [os.path.join(LOCAL_DR_PATH, 'test.txt'),
                  os.path.join(LOCAL_DR_PATH, 'test_1991.cfg.zip'),
                  os.path.join(LOCAL_DR_PATH, 'test_1998.cfg.zip'),
                  os.path.join(LOCAL_DR_PATH, 'test_2013.cff.zip'),
                  os.path.join(LOCAL_DR_PATH, 'test_2013.cfg.zip')]
    
    assert common.dir_list_diff(files, LOCAL_DR_PATH) == files_diff


def test_get_trigger_time():
    test_time = '20010203_040508'
    
    assert common.get_trigger_time(os.path.join(LOCAL_DR_PATH, 'test_1991.cfg')) == test_time
    assert common.get_trigger_time(os.path.join(LOCAL_DR_PATH, 'test_1998.cfg')) == test_time
    assert common.get_trigger_time(os.path.join(LOCAL_DR_PATH, 'test_2013.cfg')) == test_time
    assert common.get_trigger_time(os.path.join(LOCAL_DR_PATH, 'test_2013.cff')) == test_time
    
    assert common.get_trigger_time(os.path.join(LOCAL_DR_PATH, 'test_1991.cfg.zip')) == test_time
    assert common.get_trigger_time(os.path.join(LOCAL_DR_PATH, 'test_1998.cfg.zip')) == test_time
    assert common.get_trigger_time(os.path.join(LOCAL_DR_PATH, 'test_2013.cfg.zip')) == test_time
    assert common.get_trigger_time(os.path.join(LOCAL_DR_PATH, 'test_2013.cff.zip')) == test_time


def test_file_attr_str_format():
    file_list = ()
    format_str_len = (8, 8, 8)
    
    assert common.file_attr_format_str_len(file_list) == format_str_len
    
    file_list = (('file.txt', 18732, 123456789),
                 ('COMTRADE/rec_123456.zip', 10000, 1625804730.000),
                 ('test_file.cfg', 0, 389572.1),
                 ('events.log', 18273746, 102938456))
    format_str_len = (24, 16, 16)
    
    assert common.file_attr_format_str_len(file_list) == format_str_len
