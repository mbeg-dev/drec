schema = {
    'GENERAL': {
        'required': True,
        'type': 'dict',
        'schema': {
            'substation': {
                'required': True,
                'type': 'string',
                'empty': False
            },
            'root_path': {
                'required': True,
                'type': 'string',
                'empty': False
            },
            'dir_path': {
                'required': True,
                'type': 'string',
                'empty': False,
                'supported_tags': [
                    '<ROOT_PATH>',
                    '<SUBSTATION>',
                    '<NAME>',
                    '<BAY>',
                    '<LOCATION>',
                    '<DEVICE>',
                    '<COMMENT>'
                ]
            },
            'log_path': {
                'required': True,
                'type': 'string',
                'empty': False,
                'supported_tags': ['<ROOT_PATH>', '<SUBSTATION>']
            },
            'protocol': {
                'required': False,
                'type': 'string',
                'allowed': ['IEC61850', 'FTP'],
                'empty': False
            },
            'dev_port': {
                'required': False,
                'type': 'integer',
                'min': 1,
                'max': 65535
            },
            'dev_dir': {
                'required': False,
                'type': 'string'
            },
            'user': {
                'required': False,
                'type': 'string'
            },
            'password': {
                'required': False,
                'type': 'string'
            },
            'con_timeout': {
                'required': False,
                'type': 'integer',
                'min': 0
            },
            'req_timeout': {
                'required': False,
                'type': 'integer',
                'min': 0,
                'max': 4294967
            },
            'poll_timeout': {
                'required': False,
                'type': 'integer',
                'min': 0
            },
            'ret_timeout': {
                'required': False,
                'type': 'integer',
                'min': 0
            },
            'no_retry': {
                'required': False,
                'type': 'integer',
                'min': 0
            },
            'dev_tz': {
                'required': False,
                'type': 'string',
                'empty': False
            },
            'local_tz': {
                'required': False,
                'type': 'string',
                'empty': False
            }
        }
    },
    'DEVICE': {
        'required': True,
        'type': 'list',
        'schema': {
            'type': 'dict',
            'schema': {
                'protocol': {
                    'required': False,
                    'type': 'string',
                    'allowed': ['IEC61850', 'FTP'],
                    'empty': False
                },
                'dev_address': {
                    'required': True,
                    'type': 'string',
                    'regex': '^(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$',
                    'dependencies_protocol': ['IEC61850', 'FTP'],
                    'dependencies_path': True
                },
                'dev_port': {
                    'required': False,
                    'type': 'integer',
                    'min': 1,
                    'max': 65535,
                    'dependencies_protocol': ['IEC61850', 'FTP']
                },
                'dev_dir': {
                    'required': False,
                    'type': 'string',
                    'dependencies_protocol': ['IEC61850', 'FTP']
                },
                'user': {
                    'required': False,
                    'type': 'string',
                    'dependencies_protocol': ['FTP']
                },
                'password': {
                    'required': False,
                    'type': 'string',
                    'dependencies_protocol': ['FTP']
                },
                'con_timeout': {
                    'required': False,
                    'type': 'integer',
                    'min': 0,
                    'dependencies_protocol': ['FTP']
                },
                'req_timeout': {
                    'required': False,
                    'type': 'integer',
                    'min': 0,
                    'max': 4294967,
                    'dependencies_protocol': ['IEC61850']
                },
                'poll_timeout': {
                    'required': False,
                    'type': 'integer',
                    'min': 0,
                    'dependencies_protocol': ['IEC61850', 'FTP']
                },
                'ret_timeout': {
                    'required': False,
                    'type': 'integer',
                    'min': 0,
                    'dependencies_protocol': ['IEC61850', 'FTP']
                },
                'no_retry': {
                    'required': False,
                    'type': 'integer',
                    'min': 0,
                    'dependencies_protocol': ['IEC61850', 'FTP']
                },
                'name': {
                    'required': False,
                    'type': 'string',
                    'empty': True
                },
                'bay': {
                    'required': False,
                    'type': 'string',
                    'empty': True
                },
                'location': {
                    'required': False,
                    'type': 'string',
                    'empty': True
                },
                'device': {
                    'required': False,
                    'type': 'string',
                    'empty': True
                },
                'comment': {
                    'required': False,
                    'type': 'string',
                    'empty': True
                },
                'dev_tz': {
                    'required': False,
                    'type': 'string',
                    'empty': False,
                    'dependencies_protocol': ['FTP']
                },
                'local_tz': {
                    'required': False,
                    'type': 'string',
                    'empty': False,
                    'dependencies_protocol': ['IEC61850', 'FTP']
                }
            }
        }
    }
}
