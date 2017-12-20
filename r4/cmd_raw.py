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
                            help="optional: range of first and last event")

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


        parser.add_argument("-quiet", dest='quiet',
                            action='store_true', required=False,
                            help="only print content of events and nothing else")


        parser.set_defaults(cls=CmdRaw)


    def run(self, db=False, inrange=None, inhost=None,
            print_proc=False, print_parent=False, print_cmd=False, print_file=False, print_reg=False,
            filter=False, quiet=False, **kwargs):
        db = Config.get_database(db)

        db = Database(db)
        if not quiet:
            db.print_statistics()
        else:
            db.get_db_stat()


        # find hostnames with valid events
        hostdf, hostdict = db.get_hostnames(count_events=False)
#        print(hostdf)
#        print(hostdict)

        # is supplied host a valid hosts?
        hostkey = None
        if int(inhost[0]) in hostdict:
            hostkey = inhost[0]
        else:
            print(inhost[0], "not in database?")
            exit(1)

        # range
        if not inrange:
            fromid = int(db.stat[MIN_ID])
            toid   = int(db.stat[MAX_ID])
        else:
            fromid = int(inrange[0])
            toid   = int(inrange[1])

        if not quiet:
            print("\nprocessing", fromid, "-", toid)
        dr4 = DatabaseReader4(db, hostkey)


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
