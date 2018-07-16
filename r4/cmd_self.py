from pprint import pprint

from cybertrap.database import Database
from cybertrap.database_reader4 import DatabaseReader4
from cybertrap.dbconst import *
from cybertrap.filter import Filter
from cybertrap.row4 import row2dict

from r4.cmdtemplate import CommandTemplate
from r4.model_cmp4b import ModelCmp4b
from r4.modeltemplate import ModelTemplate
from r4.runsql4 import RunSQL4
from util.config import Config
from util.conv import parse_datetimestring_to_dt, dt_to_str
import time
import datetime as dt
from copy import deepcopy

from r4.runself4 import RunSelf4


class CmdSelf(CommandTemplate):
    NAME = 'selfcmp'
    HELP = 'run self comparison'

    @staticmethod
    def add_subparser(subparsers):
        parser = subparsers.add_parser(CmdSelf.NAME,
                                       aliases=['self'],
                                       help=CmdSelf.HELP)


        parser.add_argument("-d", metavar=('str','num'), dest='indb', nargs=2, required=True,
                            help="database alias, hostid")

        parser.add_argument("-ref", metavar=('xxx','xxx'), dest='inref', nargs='+', required=True,
                            help="first, last event")

        parser.add_argument("-from", metavar=('event'), dest='infrom', required=False, help="force start processing from")

        parser.add_argument("-int", metavar=('sec'), dest='ininter', required=True,  help="analysis interval in seconds")

        parser.add_argument("-quiet", dest='quiet', action='store_true', required=False, help="be quieter")

        parser.set_defaults(cls=CmdSelf)


    def _sanity_check_range_(self, db, inrange, quiet):
        if int(inrange[0]) !=0:
            if int(inrange[0])<int(db.stat[MIN_ID]):
                print("sanity check:", inrange[0],"min db event is lower than first range event",db.stat[MIN_ID])
                exit(1)

        if int(inrange[1]) !=0:
            if int(db.stat[MAX_ID])<int(inrange[1]):
                print("sanity check:", "max db event", db.stat[MAX_ID], "is smaller than max range", inrange[1])
                exit(1)

        if not quiet:
            print("processing", inrange[0], "-", inrange[1])

        return True




    def run(self, indb=None, inref=None,
            ininter=None, infrom=None,
            quiet=False,
            **kwargs):

#        print(indb)
#        print(inref)
#        print(ininter)
#        print(infrom)

        if len(inref) % 2 ==1: print("error: invalid ref range, not even number of arguments?"); exit(1)

        db = indb[0]
        host = indb[1]

        fromevent = infrom

        if type(fromevent) is not int:

            s = RunSelf4(db, host, quiet)

            if fromevent is None:    # nothing passed, find startevent from database end
                fromevent = int(s.substract_from_max_event(int(ininter)))
            elif not fromevent.isdigit():    # if on first run is timestamp string, convert to event number
                fromevent = RunSelf4._convert_start_time_to_event_number_(s.dr, s.host, fromevent, s.quiet)

            fromevent = int(fromevent)
            s.shutdown()


        while True:
            now = dt.datetime.now()
#            if not quiet:
            print("*** It is now", dt_to_str(now)+" ")  #, end=''
            s = RunSelf4(db, host, quiet)

            if fromevent<int(s.max_event):  # new events in database?
                if not quiet:
                    print("=== REFERENCE RANGE ===")

                copyref = deepcopy(inref)
                s.consume_reference(copyref)

                if not quiet:
                    print("=== COMPARISON RANGE ===")
                s.consume_events(fromevent, int(s.max_event), False)
                s.run_evaluate()

                if not quiet:
                    print("=== RESULTS ===")
                time_start = time.time()
                s.model2.pretty_print_for_humans(72)
                timespan = time.time()-time_start
                if not quiet:
                    print("{:.2f}".format(timespan)+"s: details printout")

                fromevent = int(s.max_event)+1

            else:
                if not quiet:
                    print(" - no new events in database, last", s.max_event, "< expected next", str(fromevent), " ...sleeping")

            s.shutdown()

            time.sleep(int(ininter))
