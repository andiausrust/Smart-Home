from pprint import pprint

from cybertrap.database import Database
from cybertrap.database_reader4 import DatabaseReader4
from cybertrap.dbconst import *
from cybertrap.filter import Filter
from cybertrap.row4 import row2dict

from r4.cmdtemplate import CommandTemplate
from r4.model_cmp4 import ModelCmp4
from r4.runsql4 import RunSQL4
from util.config import Config
import time


class CmdRun(CommandTemplate):
    NAME = 'run'
    HELP = 'run a model on data traces'

    @staticmethod
    def add_subparser(subparsers):
        parser = subparsers.add_parser(CmdRun.NAME,
                                       aliases=['run'],
                                       help=CmdRun.HELP)


        parser.add_argument("-d1", metavar="dbalias", dest='indb1', required=True,
                            help="database alias")

        parser.add_argument("-d2", metavar="dbalias", dest='indb2', required=False,
                            help="database2 alias")


        parser.add_argument("-r1", metavar="num", dest='inrange1', nargs=3, required=False,
                            help="hostid, first, last event")

        parser.add_argument("-r2", metavar="num", dest='inrange2', nargs=3, required=False,
                            help="hostid, first, last event")

        parser.add_argument("-quiet", dest='quiet',
                            action='store_true', required=False,
                            help="be quieter on database stats")

        parser.add_argument("-res", metavar="num", dest='result', required=False,
                            help="result number (0 for help)")

        parser.set_defaults(cls=CmdRun)


    # if run from command line
    def _sanity_check_(self, indb, inrange, quiet):

        db = Database(Config.get_database(indb))
        if not quiet:
            db.print_statistics()
        else:
            db.get_db_stat()

        # if no range passed use min/max event of database
        if not inrange:
            fromid1 = int(db.stat[MIN_ID])
            toid1   = int(db.stat[MAX_ID])
        else:
            fromid1 = int(inrange[1])
            toid1   = int(inrange[2])

        if not quiet:
            print("processing", fromid1, "-", toid1)
            print("")
        return (db, inrange[1], inrange[2])


    def run(self, indb1=False, indb2=False,
            inrange1=None, inrange2=None,
            result=None, quiet=False,
            **kwargs):

        # inrange = [hostid, fromid, toid]
        db1, inrange1[1], inrange1[2] = self._sanity_check_(indb1, inrange1, quiet)
        db2, inrange2[1], inrange2[2] = self._sanity_check_(indb2, inrange2, quiet)

        dr1 = DatabaseReader4(db1, inrange1[0])
        dr2 = DatabaseReader4(db2, inrange2[0])

        model1 = ModelCmp4(str(inrange1[0]), str(indb1))  # hostid, name
        model2 = ModelCmp4(str(inrange2[0]), str(indb2))  # hostid, name

        model1.set_other(model2)
        model2.set_other(model1)

        if result and int(result)==0:  # just print help and early exit
            model1.print_result(result)
            exit(0)


        run = RunSQL4(dr1, dr2, quiet)
        run.run_events(model1, model2, inrange1[1:3], inrange2[1:3])

        if result:
            print("\n  ", inrange1[0], "===>", model1.hostname + ":")
            model1.print_result(result)

            print("\n  ", inrange2[0], "===>", model2.hostname + ":")
            model2.print_result(result)
