from cybertrap.dbconst import *
from pprint import pprint


def row2dict(row):
    """ Convert a database row coming from Postgres to a Python dictionary.
     Some type casts are actually NOPs, however if the database somehow
     changes it breaks here and not later"""
    d = {}
    #print(row)

    d[ID]           = str(row[ID])
    d[TYPE_ID]      = int(row[TYPE_ID])
    if HOSTNAMES_ID in row:   # 2016 format
        d[HOSTNAMES_ID] = int(row[HOSTNAMES_ID])
    else:                     # 2017 format
        d[HOSTNAMES_ID] = int(row[CT_UNITS_ID])
    d[PID]          = int(row[PID])  # only need for stray events pointing to reboot

    d[PROCESS_NAME] = str(row[PROCESS_NAME]).lower()

    d[TIME]         = row[TIME]
#    d[TIME].replace(tzinfo=None)

    if row[PARENT_ID] is None:
        d[PARENT_ID] = None
    else:
        d[PARENT_ID] = str(row[PARENT_ID])

    if row[PARENT_PROCESS_NAME] is None:
        d[PARENT_PROCESS_NAME] = None
    else:
        d[PARENT_PROCESS_NAME] = str(row[PARENT_PROCESS_NAME]).lower()


    if row[GRANDPARENT_ID] is None:
        d[GRANDPARENT_ID] = None
    else:
        d[GRANDPARENT_ID] = str(row[GRANDPARENT_ID])

    if row[GRANDPARENT_PROCESS_NAME] is None:
        d[GRANDPARENT_PROCESS_NAME] = None
    else:
        d[GRANDPARENT_PROCESS_NAME] = str(row[GRANDPARENT_PROCESS_NAME]).lower()


    d[SEQUENCE_ID]  = int(row[SEQUENCE_ID])
    type_id = d[TYPE_ID]

    if type_id == PROCESS:
        d[DOMAIN_NAME]       = str(row[DOMAIN_NAME]).lower()
        d[USER_NAME]         = str(row[USER_NAME]).lower()
        d[COMMAND_LINE]      = str(row[COMMAND_LINE]).lower()
        d[WORKING_DIRECTORY] = str(row[WORKING_DIRECTORY]).lower()

    elif type_id == THREAD:
        ### FIXME -> check first if database schema changed!
        pass
#        d[TARGET_PID]    = int(row[TARGET_PID])
#        d[THREAD_ID]     = int(row[THREAD_ID])
#        d[TRG_PROC_NAME] = str(row[TRG_PROC_NAME]).lower()

    elif type_id == NETWORK:
        ### FIXME -> check first if database schema changed!
#        pass
#        d[PROTOCOL_ID]       = int(row[PROTOCOL_ID])
#        d[LOCAL_IP_ADDRESS]  = str(row[LOCAL_IP_ADDRESS])
#        d[LOCAL_PORT]        = int(row[LOCAL_PORT])
        d[REMOTE_IP_ADDRESS] = str(row[REMOTE_IP_ADDRESS])
        d[REMOTE_PORT]       = int(row[REMOTE_PORT])
#        d[IS_CONNECTION_OUTGOING] = row[IS_CONNECTION_OUTGOING]
#        d[EVILNESS]    = bool(EVILNESS)

    elif type_id == REGISTRY:
        rowtype_string = row[TYPE_STRING]
        if rowtype_string   == 'RegNtPreSetValueKey':
            d[TYPE_STRING] = REG_SET
        elif rowtype_string == 'RegNtPostCreateKeyEx':
            d[TYPE_STRING] = REG_CREATE
        else:
            print('help! unknown/unimplemented registry op: ' + rowtype_string)
            quit()

        d[PATH] = str(row[PATH]).lower()
        d[KEY]  = str(row[KEY]).lower()
        d[DATA] = bytes(row[DATA])

    elif type_id == FILE:
        rowtype = row[FILEOP]
        if rowtype   == 'CREATE':
            d[TYPE] = CREATE
        elif rowtype == 'READ':
            d[TYPE] = READ
        elif rowtype == 'WRITE':
            d[TYPE] = WRITE
        elif rowtype == 'RENAME':
            d[TYPE] = RENAME
        elif rowtype == 'DELETE':
            d[TYPE] = DELETE
        elif rowtype == 'SUPERSEDE':
            d[TYPE] = SUPERSEDE
        elif rowtype == 'WRITE_PAGING':
            d[TYPE] = WRITE_PAGING
        elif rowtype == 'READ_PAGING':
            d[TYPE] = READ_PAGING
        elif rowtype == 'MMAP_READ':
            d[TYPE] = MMAP_READ
        elif rowtype == 'MMAP_READ_WRITE':
            d[TYPE] = MMAP_READ_WRITE
        elif rowtype == 'MMAP_WRITE':
            d[TYPE] = MMAP_WRITE
        else:
            print('help! unknown/unimplemented file operation: ' + str(d[ID]) +" "+str(rowtype) )
            quit()

        d[SRC_FILE_NAME] = str(row[SRC_FILE_NAME]).lower()
        d[DST_FILE_NAME] = str(row[DST_FILE_NAME]).lower()

    else:
        print('help! unknown Cybertrap event type_id:', type_id)
        pprint(row)
        quit()

    return d
