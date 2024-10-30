# README drec

This file is part of the documentation of **drec** - disturbance record download.

Content:

* [Overview](#Overview)
  * [IEC 61850](#IEC-61850)
  * [FTP](#FTP)
* [libIEC61850](#libIEC61850)
* [Building the library](#Building-the-library)
  * [Building libIEC61850 library](#Building-libIEC61850-library)
  * [Building Cython wrapper](#Building-Cython-wrapper)
  * [Clean](#Clean)
* [IEC 61850 MMS file transfer client](#IEC-61850-MMS-file-transfer-client)
* [Configuration file](#Configuration-file)
  * [Format description](#Format-description)
  * [Parameter description](#Parameter-description)
* [Using drec](#Using-drec)
  * [drec user and group](#drec-user-and-group)
  * [Command line usage](#Command-line-usage)
* [Supervisord](#Supervisord)
  * [Supervisord configuration](#Supervisord-configuration)
  * [drec process configuration](#drec-process-configuration)
    * [Single substation process configuration example with one protocol](#Single-substation-process-configuration-example-with-one-protocol)
    * [Single substation process configuration example with multiple protocols](#Single-substation-process-configuration-example-with-multiple-protocols)
    * [Multiple substation process configuration example](#Multiple-substation-process-configuration-example)
  * [Other software process configuration](#Other-software-process-configuration)


## Overview

drec downloads disturbance records from intelligent electronic devices (IEDs) via IEC 61850 MMS file transfer using libIEC61850 library or via FTP protocol.

The most common disturbance record file format for storing oscilographic and status data is COMTRADE. More details can be found on the following link:

[Wikipedia COMTRADE](https://en.wikipedia.org/wiki/Comtrade)

drec is written in Python 3 and Cython. Except Python standard library the following Python external modules are used:

* [PyYAML](https://pypi.org/project/PyYAML/)
* [Cerberus](https://pypi.org/project/Cerberus/)

Centralized disturbance record collection and archiving system can be created when drec is combined with Supervisord.


### IEC 61850

IEC 61850 is an international standard defining communication protocols for IEDs at electrical substations. drec uses only a small portion of IEC 61850 protocol called MMS file transfer for disturbance record download.

File class defines:

* File attribute name and type
  * FileName (VISIBLE STRING255)
  * FileSize (INT32U)
  * LastModified (TimeStamp)
* Services
  * GetFile - data transfer from IED (server) to client
  * SetFile - data file transfer from client to IED (server)
  * DeleteFile - delete file on IED (server)
  * GetFileAttributeValues - list of available files and directories on IED (server)

List of available files and directories is obtained with *GetFileAttributeValues* command and files are downloaded using *GetFile* command.

> **Note**
>
> FileName = \[Path Sep\] File \[.Ext\]  
> With:
>> Path - Subdirectory with max length of 32 characters  
>> Sep - "/" or "\" - always the same on one IED (server)  
>> Ext - Alphanumeric string with maximum length of 3 characters  
>> File - String of maximum length of 64 characters with exception of characters "\" or "/"
>
> FileSize - size of the file in bytes. FileSize = 0 if file is created on-the-fly or empty.
>
> LastModified - TimeStamp in Unix epoch format


### FTP

The File Transfer Protocol (FTP) is a standard communication protocol used for the transfer of computer files from a server to a client on a computer network. FTP protocol was extended over time with multiple RFC standards.

Some commands defined by RFC 959:

* CWD - Change working directory
* DELE - Delete file
* HELP - Returns usage documentation on a command if specified, else a general help document is returned
* LIST - Returns information of a file or directory if specified, else information of the current working directory is returned
* MKD - Make directory
* NLST - Returns a list of file names in a specified directory
* PASS - Authentication password
* RETR - Retrieve a copy of the file
* RMD - Remove a directory
* USER - Authentication username

Some commands defined by RFC 3659:

* MDTM - Return the last-modified time of a specified file
* MLSD - Lists the contents of a directory in a standardized machine-readable format
* MLST - Provides data about exactly the object named on its command line in a standardized machine-readable format
* SIZE - Return the size of a file

Most FTP servers support set of commands defined by RFC 959. FTP *LIST* command is suitable for user terminal usage but it's not suitable for scripting/programming since it returns non-standardized response. Therefore
drec tries *MLSD* command to read available files from IED (with included size and timestamp information) but if IED doesn't support the command than *NLST* command is used to obtain only a list of files. Since *NLST* command provides only list of files *SIZE* command is used to get file size and *MDTM* command is used to get the timestamp. If *SIZE* command is not supported file size is set to 0 and if *MDTM* command is not supported timestamp is set to local time when *NLST* command was used.


## libIEC61850

libiec61850 is an open-source (GPLv3 - The GNU General Public License v3.0) implementation of an IEC 61850 client and server library implementing the protocols MMS, GOOSE and SV. It is implemented in C (according to the C99 standard) to provide maximum portability.

More details can be found on the following links:

* [libIEC61850 home page](https://libiec61850.com/)
* [libIEC61850 GitHub](https://github.com/mz-automation/libiec61850)

Only MMS file transfer is used to download disturbance records from IEDs.


## Building the library

Create source code directory:

`mkdir /opt/drec`

Download drec source and copy it in `/opt/drec` directory.

> **Note**
>
> drec doesn't have to be installed in `/opt/drec` directory. Any directory can be used but modify commands bellow accordingly.


### Building libIEC61850 library

Download libiec61850-*.tar.gz from libIEC61850 home page or GitHub. Unpack the library in directory `opt/drec/iec61850/libiec61850/src/` using the following commands:

`tar -xf /opt/drec/iec61850/libiec61850/src/libiec61850-*.tar.gz`


Open library directory:

`cd /opt/drec/iec61850/libiec61850/src/libiec61850-*`


Build and install the library:

`make dynlib && make install`


> **Note**
>
> For version 1.4.2.1 of the library copy hal_base.h to source directory:
>
> `cp hal/inc/hal_base.h .install/source/`


### Building Cython wrapper

Copy library and headers from libiec61850-*/.install to drec/iec61850/libiec61850/src directory:

`cp /opt/drec/iec61850/libiec61850/src/libiec61850-*/.install/* /opt/drec/iec61850/libiec61850/src/`


Build Cython source code:

`python3 /opt/drec/iec61850/libiec61850/setup.py build_ext --inplace`


> **Note**
>
> If Cython 3.x.x version is used than modification in client wrapper source file is necesary `drec/iec61850/libiec61850/iec61850_client.pyx`.
> Add `noexcept` at the end of `cdef bool __downloadHandler(void* parameter, uint8_t* buffer, uint32_t bytesRead):`.


### Clean

Remove libIEC61850 library

```
rm /opt/drec/iec61850/libiec61850/src/libiec61850-*.tar.gz
rm -r /opt/drec/iec61850/libiec61850/src/libiec61850-*
```


## IEC 61850 MMS file transfer client

IEC 61850 MMS file transfer client command usage:

`usage: client-iec61850 [-h] [-p PORT] [-t TIMEOUT] [-c {dir,info,get,set,del}] [-s SRC] [-d DEST] host`


Detail parameters can be obtained using -h or --help argument:

`python3 client-iec61850 -h` or `./client-iec61850 -h`


IEC 61850 MMS file transfer client help with parameter description:

```
usage: client-iec61850 [-h] [-p PORT] [-t TIMEOUT] [-c {dir,info,get,set,del}] [-s SRC] [-d DEST] host

Client for IEC 61850 MMS file transfer

positional arguments:
  host                  Hostname/IP address

options:
  -h, --help            show this help message and exit
  -p PORT, --port PORT  Port number. Default 102
  -t TIMEOUT, --timeout TIMEOUT
                        Request timeout in miliseconds UINT32. Default 5000 ms.
  -c {dir,info,get,set,del}, --command {dir,info,get,set,del}
                        Client commands. Default dir.
                          dir  - list file tree
                          info - information about specific file/directory
                                   -s SRC  - path to IED file/directory
                          get  - download file from IED
                                   -s SRC  - path to IED file
                                   -d DEST - filename or path to local file (optional)
                          set  - upload file to IED
                                   -s SRC  - path local file
                                   -d DEST - filename or path to IED file (optional)
                          del  - delete file from IED
                                   -s SRC  - path to IED file
  -s SRC, --src SRC     Source file/directory in combination with commnads: info, get, set and del
  -d DEST, --dest DEST  Destination file in combination with commnads: get and set

Examples:

List all files on IED
    client-iec61850 HOST or client_iec61850 -c dir HOST

Information about specific directory
    client-iec61850 -c info -s IED_DIR_PATH HOST

Information about specific file
    client-iec61850 -c info -s IED_FILE_PATH HOST

Download file from IED root to current directory
    client-iec61850 -c get -s IED_FILE_NAME HOST

Download file from IED to current directory
    client-iec61850 -c get -s IED_FILE_PATH HOST

Download file from IED to current directory and change file name
    client-iec61850 -c get -s IED_FILE_PATH -d LOCAL_FILE_NAME HOST

Download file from IED to specified current directory and change file name
    client-iec61850 -c get -s IED_FILE_PATH -d LOCAL_FILE_PATH HOST

Upload local file to IED root
    client-iec61850 -c set -s LOCAL_FILE_PATH HOST

Upload local file to IED root and change file name
    client-iec61850 -c set -s LOCAL_FILE_PATH -d IED_FILE_NAME HOST

Upload local file to IED drectory and change file name
    client-iec61850 -c set -s LOCAL_FILE_PATH -d IED_FILE_PATH HOST

Delete file from IED root
    client-iec61850 -c del -s IED_FILE_NAME HOST

Delete file from IED
    client-iec61850 -c del -s IED_FILE_PATH HOST
```


## Configuration file

Configuration file for devices in substation is written in yaml format. Configuration file examples for IEC 61850 and FTP protocol with parameter description can be found in config directory.


> **Note**
>
> Even though it's possible to use single configuration file for devices with different communication protocols it's recommended to use only one communication protocol in the configuration file.
>
> When used with Supervisord separate process can be configured for every communication protocol which are executed simultaneously or single process can be configured per substation where configuration files for different protocols are executed consecutively.


### Format description

Configuration file consists of two sections GENERAL and DEVICES. File structure is shown bellow.

```
GENERAL:
    substation:     string              required
    root_path:      string              required
    dir_path:       string              required
    log_path:       string              required
    protocol:       string              required/optional
    dev_port:       unsigned int        recommended/optional
    dev_dir:        string              optional
    user:           string              recommended/optional
    password:       string              recommended/optional
    con_timeout:    unsigned int        optional
    req_timeout:    unsigned int        optional
    poll_timeout:   unsigned int        optional
    ret_timeout:    insigned int        optional
    no_retry:       unsigned int        optional
    dev_tz:         string              optional
    local_tz:       string              recommended/optional

DEVICES:
  - protocol:       string              required/optional
    dev_address:    string              required
    dev_port:       unsigned int        recommended/optional
    dev_dir:        string              optional
    user:           string              recommended/optional
    password:       string              recommended/optional
    con_timeout:    unsigned int        optional
    req_timeout:    unsigned int        optional
    poll_timeout:   unsigned int        optional
    ret_timeout:    insigned int        optional
    no_retry:       unsigned int        optional
    name:           string              required/optional
    bay:            string              required/optional
    location:       string              required/optional
    device:         string              required/optional
    comment:        string              required/optional
    dev_tz:         string              optional
    local_tz:       string              recommended/optional
```

Parameters used only in GENERAL section are parameters used for all devices in the whole substation:

* `substation`
* `root_path`
* `dir_path`
* `log_path`


Parameters used only in DEVICES section are paramters per device:

* `dev_address`
* `name`
* `bay`
* `location`
* `device`
* `comment`


Parameters which can be used in GENERAL or DEVICES section are listed bellow:

* `protocol`
* `dev_port`
* `dev_dir`
* `user`
* `password`
* `con_timeout`
* `req_timeout`
* `poll_timeout`
* `ret_timeout`
* `no_retry`
* `dev_tz`
* `local_tz`

If parameter is used in GENERAL section than parameter is used for all devices in substation and there is no need to set it per device. But if the same parameter is set in GENERAL and DEVICE section than parameter in DEVICE superseeds parameter in GENERAL section.

If parameter is not set in GENERAL or DEVICE section than default hardcoded value will be used. For better control over parameters it's recommended to manually set all parameters in GENERAL section.


### Parameter description

Configuration file parameter description:

***`substation:`***

* Type: string
* Description: Substation name can be used in `dir_path` and `log_path` using tag `<SUBSTATION>`
* Usage: Required only in GENERAL section
* Protocol: any (not protocol specific)


***`root_path:`***

* Type: string
* Description: Root path for disturbance record storage can be used in `dir_path` and `log_path` parameters using tag `<ROOT_PATH>`
* Usage: Required only in GENERAL section
* Protocol: any (not protocol specific)


***`dir_path:`***

* Type: string
* Description: User defined directory storage path using tags
* Usage: Required only in GENERAL section
* Protocol: any (not protocol specific)
* Supported tags: `<ROOT_PATH>`, `<SUBSTATION>`, `<NAME>`, `<BAY>`, `<LOCATION>`, `<DEVICE>`, `<COMMENT>`


***`log_path:`***

* Type: string
* Description: User defined log storage path using tags described bellow. Log file per substation is used.
* Usage: Required only in GENERAL section
* Protocol: any (not protocol specific)
* Supported tags: `<ROOT_PATH>`, `<SUBSTATION>`


***`protocol:`***

* Type: string
* Description: Configured communication protocol in GENERAL section is common for all devices in config file
* Usage: Required in GENERAL or DEVICES section
* Supported protocols: `IEC61850`, `FTP`


***`dev_address:`***

* Type: string
* Description: IP address or hostname
* Usage: Required in DEVICES section
* Protocol: `IEC61850`, `FTP`


***`dev_port:`***

* Type: unsigned int
* Description: TCP port (0-65535)
* Usage: Optional in GENERAL or DEVICES section
* Protocol: `IEC61850`, `FTP`
* Default:
  * IEC 61850: 102
  * FTP\: 21


***`dev_dir:`***

* Type: string
* Description: Device directory (path) for storing disturbance records
* Usage: Optional in GENERAL or DEVICES section
* Protocol: `IEC61850`, `FTP`
* Default: COMTRADE


***`user:`***

* Type: string
* Description: Username login
* Usage: Optional in GENERAL or DEVICES section
* Protocol: `FTP`
* Default: anonymous


***`password:`***

* Type: string
* Description: Password login
* Usage: Optional in GENERAL or DEVICES section
* Protocol: `FTP`
* Default: empty password


***`con_timeout:`***

* Type: unsigned int
* Description: Connection timeout in seconds
* Usage: Optional in GENERAL or DEVICES section
* Protocol: `FTP`
* Default: 60 s


***`req_timeout:`***

* Type: unsigned int
* Description: Request timeout in seconds. Request timeout may have to be changed for slow connections.
* Usage: Optional in GENERAL or DEVICES section
* Protocol: `IEC61850`
* Parameter range: 0-4294967 (libIEC61850 internally uses request timeout parameter as 32-bit unsigned int in miliseconds)
* Default: 5 s


***`poll_timeout:`***

* Type: unsigned int
* Description: Polling timeout between file downloads in seconds. Timeout may have to be changed for slow connections to release connections resources between polls. Timeout should be shorter than connection timeout.
* Usage: Optional in GENERAL or DEVICES section
* Protocol: `IEC61850`, `FTP`
* Default: 0 s


***`ret_timeout:`***

* Type: unsigned int
* Protocol: `IEC61850`, `FTP`
* Description: Retry timeout in seconds
* Usage: Optional in GENERAL or DEVICES section
* Default: 10 s


***`no_retry:`***

* Type: unsigned int
* Description: Number of retries on exception `ConnectionError`
* Usage: Optional in GENERAL or DEVICES section
* Protocol: `IEC61850`, `FTP`
* Default: 1


***`name:`***

* Type: string
* Description: Bay name
* Usage: Required in DEVICES section if `<NAME>` tag is used in `dir_path`
* Protocol: `IEC61850`, `FTP`


***`bay:`***

* Type: string
* Description: Bay code (code =)
* Usage: Required in DEVICES section if `<BAY>` tag is used in `dir_path`
* Protocol: `IEC61850`, `FTP`


***`location:`***

* Type: string
* Description: Location code (code +)
* Usage: Required in DEVICES section if `<LOCATION>` tag is used in `dir_path`
* Protocol: `IEC61850`, `FTP`


***`device:`***

* Type: string
* Description: Device code (code -)
* Usage: Required in DEVICES section if `<DEVICE>` tag is used in `dir_path`
* Protocol: `IEC61850`, `FTP`


***`comment:`***

* Type: string
* Description: Comment
* Usage: Required in DEVICES section if `<COMMENT>` tag is used in `dir_path`
* Protocol: `IEC61850`, `FTP`


***`dev_tz:`***

* Type: string
* Description: Device timezone
* Usage: Optional in GENERAL or DEVICES section
* Protocol: `FTP`
* Default: UTC


***`local_tz:`***

* Type: string
* Description: Local timezone
* Usage: Optional in GENERAL or DEVICES section
* Protocol: `IEC61850`, `FTP`
* Default: UTC


> **Note**
>
> [List of tz database time zones](https://en.wikipedia.org/wiki/List_of_tz_database_time_zones)


***Parameter setting hints***

* `req_timeout` - default value should be increased for slow connections such as radio communication
* `poll_timout` and `ret_timeout` - default value should be increased for slow connections


***Disturbance record file structure***

Disturbance record files are saved with original file name but with date and time prefix in format YYYYMMDD_HHMMSS with local timezone. Files will be saved in the user defined path structure using tags. All characters which are not supported tags are used as regular characters. Example of file structure:

```
<ROOT_PATH>/<SUBSTATION>/<BAY> - <NAME>/<DEVICE>
 |
 |- YYYYMMDD_HHMMSS_disturbance_record_name.dat
 |- YYYYMMDD_HHMMSS_disturbance_record_name.cfg
 |- YYYYMMDD_HHMMSS_disturbance_record_name.hdr
```

> **Note**
>
> When disturbance records are downloaded from IED in COMTRADE format than trigger timestamp is read from the config file and used in the file name but if it is not possible to read timestamp or some other file format is used than file timestamp received from IED is used. If it is not possible to read timestamp from the IED than local time when list of available files were read from IED is used in file name.


## Using drec


### Command line usage

drec client command usage:

`usage: client [-h] [-l] [-v {DEBUG,INFO,WARNING,ERROR,CRITICAL} | -q] [-s [0-86400]] [-S [0-86400]] [-c] CONFIG [CONFIG ...]`


Detail parameters can be obtained using -h or --help argument:

`python3 client -h` or `./client -h`


drec client help with parameter description:

```
usage: client [-h] [-l] [-v {DEBUG,INFO,WARNING,ERROR,CRITICAL} | -q] [-s [0-86400]] [-S [0-86400]] [-c]
       CONFIG [CONFIG ...]

Client for disturbance record download

positional arguments:
  CONFIG                Client configuraion file(s)

options:
  -h, --help            Show this help message and exit
  -l, --loop            Run in infinitte loop
  -v, --verbose         Verbosity level {DEBUG,INFO,WARNING,ERROR,CRITICAL}. Default DEBUG.
  -q, --quiet           Quiet mode
  -s, --sleep           Delay in seconds (0-86400 s) between reading/processing CONFIG files. Default 0 seconds.
  -S, --sleep_loop      Delay in seconds (0-86400 s) between loops. Default 1 second.
  -c, --check_config    Only validate config file(s) (client is not executed)
```

Configuration files can be checked using command:

`./client -c path_to_config_file.yaml`

drec can download disturbance record files from one substation (one config file):

`./client path_to_config_file.yaml`

drec can download disturbance record files from multiple substations (multiple config files):

`./client path_to_config_file_1.yaml path_to_config_file_2.yaml`

drec can run as deamon in infinite loop. Daemon is stopped gracefully with TERM signal:

`./client -l -v INFO -s 1 -S 60 path_to_config_file.yaml`


> **Note**
>
> Termination signals **SIGTERM** and **SIGINT** are used to used to gracefully stop the process.


## Supervisord

Supervisor is a client/server system that allows its users to monitor and control a number of processes on UNIX-like operating systems.

More details can be found on the following link:

* [Supervisord](http://supervisord.org/)

Services, for example one drec service per substation, are created using supervisord.


### drec user and group

It's recommended to create drec user with nologin shell which is going to be used to run drec client to automatically download disturbance records.

`sudo groupadd drec`

`sudo useradd -m -d /storage/drec/ -g drec -s /usr/sbin/nologin -c "Disturbance record download" drec`


### Supervisord configuration

Example of supervisord.conf config file

```
; supervisor config file

[unix_http_server]
file=/var/run/supervisor.sock   ; (the path to the socket file)
chmod=0700                      ; sockef file mode (default 0700)

[inet_http_server]
port=127.0.0.1:9001
username=admin
password=admin

[supervisord]
logfile=/var/log/supervisor/supervisord.log ; (main log file;default $CWD/supervisord.log)
pidfile=/var/run/supervisord.pid            ; (supervisord pidfile;default supervisord.pid)
childlogdir=/var/log/supervisor             ; ('AUTO' child log dir, default $TEMP)

; the below section must remain in the config file for RPC
; (supervisorctl/web interface) to work, additional interfaces may be
; added by defining them in separate rpcinterface: sections
[rpcinterface:supervisor]
supervisor.rpcinterface_factory = supervisor.rpcinterface:make_main_rpcinterface

[supervisorctl]
serverurl=unix:///var/run/supervisor.sock ; use a unix:// URL  for a unix socket

; The [include] section can just contain the "files" setting. This
; setting can list multiple files (separated by whitespace or
; newlines). It can also contain wildcards. The filenames are
; interpreted as relative to this file. Included files *cannot*
; include files themselves.

[include]
files = /etc/supervisor/conf.d/*.conf
```


> **Note**
>
> The inet HTTP server is not enabled by default. If you choose to enable it, please read security warning from supervisord web site. Never expose the inet HTTP server to the public internet or intranet.


### drec process configuration

Supervisord can be used to configure process for single substation or process for multiple substations.


> **Note**
>
> **TERM** signal is used to gracefully stop the process.


#### Single substation process configuration example with one protocol

```
[program:drec_SS_110_20_kV_substation_name]
command=/opt/drec/client -l -v INFO -s 1 -S 60 /storage/drec/conf/conf_SS_110_20_kV_Substation_name.yaml
autostart=true
autorestart=true
startsecs=0
user=drec
stopsignal=TERM
stopwaitsec=30
stdout_logfile=/var/log/supervisor/drec/%(program_name)s_stdout.log
stdout_logfile_maxbytes=10MB
stdout_logfile_backups=10
stderr_logfile=/var/log/supervisor/drec/%(program_name)s_stderr.log
stderr_logfile_maxbytes=10MB
```


#### Single substation process configuration example with multiple protocols

If substation uses multiple protocols for disturbance record download than configuration file should be configured for each protocol. Configuration files for different protocols are executed consecutively.

```
/storage/drec/conf/conf_SS_110_20_kV_Substation_name_IEC61850.yaml
/storage/drec/conf/conf_SS_110_20_kV_Substation_name_FTP.yaml
```

Supervisord configuration file `command=` modification for multiple protocols in one process per substation.

```
command=bash -c "/opt/drec/client -l -v INFO -s 1 -S 60 /storage/drec/conf/conf_SS_110_10_kV_Substation_name_*.yaml"
```


#### Multiple substation process configuration example

Process with multiple configuration files can be created using list of configuration files. If multiple substations are configured within one process as list of individual substation configuration files than disturbance records are read sequentially from configured substations.

```
# SS 110/20 kV Substation 1
/storage/drec/conf/conf_SS_110_20_kV_Substation_1.yaml

# SS 110/20 kV Substation 2
/storage/drec/conf/conf_SS_110_20_kV_Substation_2.yaml

# SS 110/20 kV Substation 3
/storage/drec/conf/conf_SS_110_20_kV_Substation_3.yaml

# List of substation config files

# SS 110/20 kV Substation n
/storage/drec/conf/conf_SS_110_20_kV_Substation_n.yaml
```

Supervisord configuration file `command=` modification for multiple substations in one process.

```
# read all filenames from file not starting with comment symbol #
command=bash -c "/opt/drec/client -l -v INFO -s 1 -S 60 $(grep -v '^#' /storage/drec/conf/conf_multiple_substations)"
```


### Other software process configuration

Supervisord can be used to configure process for any cmd based software. If drec software doesn't support some functionality or communication protocol but some other cmd based software does than it's possible to configure process to download disturbance records. Example bellow is for lftp application.

***Supervisord process configuration file***

```
[program:lftp_SS_110_20_kV_substation_name]
command=/opt/lftp_script/SS_110_20_kV_Substation_name
autostart=true
autorestart=true
startsecs=0
user=drec
stopsignal=TERM
stopwaitsec=30
stdout_logfile=/var/log/supervisor/drec/%(program_name)s_stdout.log
stdout_logfile_maxbytes=10MB
stdout_logfile_backups=10
stderr_logfile=/var/log/supervisor/drec/%(program_name)s_stderr.log
stderr_logfile_maxbytes=10MB
```

***lftp script***

```
#!/bin/bash

# SS 110/20 kV Substation name

# Minimal read interval (seconds)
interval_min=120

# Max number of retries per connection
no_retries=2

# Device directory
dev_dir="/COMTRADE"

# Local download directory
local_dir="/storage/drec/SS_110_20_kV_Substation_name"

# Infinite loop
while true
do
    # Break infinite loop for signals
    trap 'break' SIGTERM SIGINT

    # Start time in epoch format (seconds)
    start_time=$(date +%s)

    # Start downloading files via FTP

    # E01 - OHL 1 - Main protection
    lftp -u user,password \
         -e "set net:max-retries $no_retries; mirror $dev_dir $local_dir/E01_OHL_1/Main_protection; bye" \
         ftp://192.168.10.101 2>&1

    # E01 - OHL 1 - Backup protection
    lftp -u user,password \
         -e "set net:max-retries $no_retries; mirror $dev_dir $local_dir/E01_OHL_1/Backup_protection; bye" \
         ftp://192.168.10.102 2>&1

    # E02 - Transformer 1 - Main 1 protection
    lftp -u user,password \
         -e "set net:max-retries $no_retries; mirror $dev_dir $local_dir/E02_Transformer_1/Main_1_protection; bye" \
         ftp://192.168.10.103 2>&1

    # E02 - Transformer 1 - Main 2 protection
    lftp -u user,password \
         -e "set net:max-retries $no_retries; mirror $dev_dir $local_dir/E02_Transformer_1/Main_2_protection; bye" \
         ftp://192.168.10.104 2>&1

    # Stop time in epoch format (seconds)
    stop_time=$(date +%s)

    # Process elapsed time (seconds)
    elapsed_time=$(( stop_time - start_time ))

    # Calculate sleep time (seconds)
    sleep_time=$(( interval_min - elapsed_time ))

    # If process execution time is shorter than minimal interval time
    # than pause new loop execution
    if (( sleep_time > 0 ))
    then
        sleep $sleep_time
    fi
done
```
