from pprint import pprint

from cybertrap.database import Database
from cybertrap.database_reader4 import DatabaseReader4
from cybertrap.dbconst import *
from cybertrap.filter import Filter
from cybertrap.row4 import row2dict

from r4.cmdtemplate import CommandTemplate
from util.config import Config
import time


class CmdRaw(CommandTemplate):
    NAME = 'raw'
    HELP = 'raw dump of primitive fields'

    @staticmethod
    def add_subparser(subparsers):
        parser = subparsers.add_parser(CmdRaw.NAME,
                                       aliases=['raw'],
                                       help=CmdRaw.HELP)
        parser.add_argument("-d", metavar="dbalias", dest='db', required=True,
                            help="database alias")

        parser.add_argument("-r", metavar="num", dest='inrange', nargs=2, required=False,
                            help="range of first and last event (optional)")

        parser.add_argument("-ho", metavar="hostid", dest='inhost', nargs=1, required=True,
                            help="id of host")


        parser.add_argument("-proc", dest='print_proc',
                            action='store_true', required=False,
                            help="print process")

        parser.add_argument("-parent", dest='print_parent',
                            action='store_true', required=False,
                            help="print parent process")


        parser.add_argument("-cmd", dest='print_cmd',
                            action='store_true', required=False,
                            help="print process command line")

        parser.add_argument("-file", dest='print_file',
                            action='store_true', required=False,
                            help="print file events")

        parser.add_argument("-reg", dest='print_reg',
                            action='store_true', required=False,
                            help="print registry events")


        parser.add_argument("-filter", dest='filter',
                            action='store_true', required=False,
                            help="apply filtering")


        parser.add_argument("-robert", dest='robert',
                            action='store_true', required=False,
                            help="dump in Robert's special format")

        parser.add_argument("-nopath", dest='nopath',
                            action='store_true', required=False,
                            help="cut path from parent executables")

        parser.add_argument("-nochildpath", dest='nochildpath',
                            action='store_true', required=False,
                            help="cut path from child executables")



        parser.add_argument("-quiet", dest='quiet',
                            action='store_true', required=False,
                            help="only print content of events and nothing else")


        parser.set_defaults(cls=CmdRaw)


    def do_robert(self, row, nopath, nochildpath):
        parent_process_name = row[PARENT_PROCESS_NAME]
        if not parent_process_name:
            parent_process_name = "UNKNOWN"

        if nopath:
            i = parent_process_name.rfind("\\")
            if i is not -1:
                parent_process_name = parent_process_name[i+1:]

        parent_id = row[PARENT_ID]
        if not parent_id:
            parent_id = str(-1)

        process_name = row[PROCESS_NAME]
        if not process_name:
            process_name = "UNKNOWN"

        if nochildpath:
            i = process_name.rfind("\\")
            if i is not -1:
                process_name = process_name[i+1:]


        id = str(row[ID])


        leadid = str(row[ID])+"  "
        leadid = ""

        if row[TYPE_ID] == PROCESS:
            print(leadid+parent_process_name+"-"+parent_id+";"+"PROCESS-CREATE"+";"+process_name)

        elif row[TYPE_ID] == FILE:
            front = leadid+parent_process_name+"-"+parent_id+";"

            if row[TYPE] == CREATE:
                print(front+"FILE-CREATE;"+row[SRC_FILE_NAME])
            elif row[TYPE] == READ:
                print(front+"FILE-READ;"+row[SRC_FILE_NAME])
            elif row[TYPE] == WRITE:
                print(front+"FILE-WRITE;"+row[SRC_FILE_NAME])
            elif row[TYPE] == DELETE:
                print(front+"FILE-DELETE;"+row[SRC_FILE_NAME])

        elif row[TYPE_ID] == REGISTRY:
            front = leadid+parent_process_name+"-"+parent_id+";"

            if row[TYPE_STRING] == REG_SET:
                print(front+"REGISTRY-SET"+";"+row[PATH]+"\\"+row[KEY])
            elif row[TYPE_STRING] == REG_CREATE:
                print(front+"REGISTRY-CREATE"+";"+row[PATH])

        elif row[TYPE_ID] == NETWORK:
            front = leadid+parent_process_name+"-"+parent_id+";"

            print(front+"NETWORK-OPEN"+";"+row[REMOTE_IP_ADDRESS]+"-"+str(row[REMOTE_PORT]))

        else:
            pass


    def run(self, db=False, inrange=None, inhost=None,
            print_proc=False, print_parent=False, print_cmd=False, print_file=False, print_reg=False,
            filter=False, quiet=False, robert=None, nopath=False, nochildpath=False, **kwargs):
        db = Config.get_database(db)

        db = Database(db)
        if not quiet:
            db.print_statistics()
        else:
            db.get_db_stat()

#         # find hostnames with valid events
#         hostdf, hostdict = db.get_hostnames(count_events=False)
# #        print(hostdf)
# #        print(hostdict)
#
#         # is supplied host a valid hosts?
#         hostkey = None
#         if int(inhost[0]) in hostdict:
#             hostkey = inhost[0]
#         else:
#             print(inhost[0], "not in database?")
#             exit(1)

        # range
        if not inrange:
            fromid = int(db.stat[MIN_ID])
            toid   = int(db.stat[MAX_ID])
        else:
            fromid = int(inrange[0])
            toid   = int(inrange[1])

        if not quiet:
            print("\nprocessing", fromid, "-", toid)
        dr4 = DatabaseReader4(db, inhost[0])


        time_start = time.time()
        resprox = dr4.read_sql(str(fromid), str(toid))
        if not quiet:
            print("after SELECT: ", resprox.rowcount, "events", "("+str(int(resprox.rowcount/ (time.time()-time_start))), "events/s)")
            print("")



        time_start = time.time()
        events_processed = 0

        while True:
            listofrows = resprox.fetchmany(size=400000)

            if len(listofrows)==0:
                break

            for rowprox in listofrows:
#                    if events_processed % 10000 == 0 and (not quiet):
#                        print(".",end='',flush=True)

                    row = row2dict(rowprox)

                    if filter:
                        Filter.run_filters(row)

                    if robert:
                        self.do_robert(row, nopath, nochildpath)
                    else:
                        if row[TYPE_ID] == PROCESS:
                            if print_proc:
                                print("P"+row[PROCESS_NAME])
                            if print_cmd:
                                print("C"+row[COMMAND_LINE])
                            if print_parent and row[PARENT_PROCESS_NAME]:
                                print("p"+row[PARENT_PROCESS_NAME])

                        elif print_file and row[TYPE_ID] == FILE:
                            print("F"+row[SRC_FILE_NAME])

                            if row[TYPE] == RENAME:
                                print("F"+row[DST_FILE_NAME])

                        elif print_reg and row[TYPE_ID] == REGISTRY:
                            print("R"+row[PATH]+'⣿'+row[KEY])

                        else:
                            pass

                    events_processed +=1

        if not quiet:
            print("\n..last event:", row[ID], row[TIME])
            print("-->", events_processed, "events", "("+str(int(events_processed/ (time.time()-time_start))), "events/s)")
