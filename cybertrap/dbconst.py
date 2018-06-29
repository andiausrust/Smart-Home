# Cybertrap database fields as Python dictionary keys

# events type_id
PROCESS  = 0
THREAD   = 1
NETWORK  = 2
REGISTRY = 3
FILE     = 4

TYPEID2STR = ['PROCESS',
              'THREAD',
              'NETWORK',
              'REGISTRY',
              'FILE']

# file ops
CREATE = 0
READ   = 1
WRITE  = 2
RENAME = 3
DELETE = 4
SUPERSEDE    = 5
WRITE_PAGING = 6
READ_PAGING  = 7
MMAP_READ    = 8
MMAP_READ_WRITE = 9
MMAP_WRITE   = 10
RENAME_SRC   = 11  # fake type, not in database
RENAME_DST   = 12  # fake type, not in database

FILEOP2STR = ['  CRE',
              'READ ',
              'WRITE',
              '  REN',
              '  DEL',
              ' SPS ',
              'WRI_P',
              'REA_P',
              'MM_RE',
              'MM_RW',
              'MM_WR',
              'REN_S',
              'REN_D']

# registry ops
REG_SET    = 0
REG_CREATE = 1

REGOP2STR = ['SET',
             'CRE']


# statistic keys
ROWS =     'rows'
MIN_ID =   'min_id'
MIN_TIME = 'min_time'
MAX_ID =   'max_id'
MAX_TIME = 'max_time'


### Cybertrap Postgres keys

# event
ID =              "id"
TYPE_ID =         "type_id"
IP_ADDRESSES_ID = "ip_addresses_id"
HOSTNAMES_ID =    "hostnames_id"
CT_UNITS_ID =     "ct_units_id"
PID =             "pid"
PROCESS_NAME =    "process_name"
TIME =            "time"
IS_BLACKLISTED =  "is_blacklisted"
SEQUENCE_ID =     "sequence_id"
PARENT_ID =           "parent_id"
PARENT_PROCESS_NAME = "parent_process_name"
GRANDPARENT_ID =           "grandparent_id"
GRANDPARENT_PROCESS_NAME = "grandparent_process_name"

# network_events
PROTOCOL_ID            = "protocol_id"
LOCAL_IP_ADDRESS       = "local_ip_address"
LOCAL_PORT             = "local_port"
REMOTE_IP_ADDRESS      = "remote_ip_address"
REMOTE_PORT            = "remote_port"
IS_CONNECTION_OUTGOING = "is_connection_outgoing"
EVILNESS =               "evilness"

# file events
TYPE =          "type"
SRC_FILE_NAME = "src_file_name"
DST_FILE_NAME = "dst_file_name"
FILEOP =        "fileop"

# process_events
PARENT_PID =        "parent_pid"
DOMAIN_NAME =       "domain_name"
USER_NAME =         "user_name"
COMMAND_LINE =      "command_line"
WORKING_DIRECTORY = "working_directory"

# thread_events
TARGET_PID =    "target_pid"
THREAD_ID =     "thread_id"
TRG_PROC_NAME = "trg_proc_name"

# registry_events
TYPE_STRING = "type_string"
PATH =        "path"
KEY =         "key"
DATA =        "data"

# hostnames
HOSTNAME = 'hostname'

DUMMY_PROCESS_NAME = r'Dummy Process Event'.lower()
SYSTEM_PROCESS_NAME = r'system'.lower()
