from pprint import pprint

from cybertrap.database import Database
from cybertrap.database_reader4 import DatabaseReader4
from cybertrap.dbconst import *
from cybertrap.filter import Filter
from cybertrap.row4 import row2dict

from r4.cmdtemplate import CommandTemplate
from r4.model_cmp4 import ModelCmp4
from r4.model_cmp4b import ModelCmp4b
from r4.modeltemplate import ModelTemplate
from r4.runsql4 import RunSQL4
from util.config import Config
import time

from util.plotme import Plotme


def getmodel4(thismodel: str) -> ModelTemplate:
    """ helper method to instantiate model by name """
    if thismodel == "cmp4":
        return ModelCmp4

    elif thismodel == "cmp4b":
        return ModelCmp4b

    elif not thismodel:
        print("Error! no model specified, choose one of:")
        print("cmp4")
        print("cmp4b")
        exit(1)

    else:
        print("Error! unknown model: " + thismodel)
        exit(1)



class CmdRun(CommandTemplate):
    NAME = 'run'
    HELP = 'run a model on data traces'

    @staticmethod
    def add_subparser(subparsers):
        parser = subparsers.add_parser(CmdRun.NAME,
                                       aliases=['run'],
                                       help=CmdRun.HELP)


        parser.add_argument("-d1", metavar=('str','num'), dest='indb1', nargs=2, required=True,
                            help="database1 alias, hostid")

        parser.add_argument("-d2", metavar=('str','num'), dest='indb2', nargs=2, required=False,
                            help="database2 alias, hostid")

        parser.add_argument("-m", metavar="modelname", dest='inmodel', required=False,
                            help="run with this model")

        parser.add_argument("-r1", metavar=('num','num'), dest='inrange1', nargs='+', required=True,
                            help="first, last event (0 0 for NOP)")

        parser.add_argument("-r2", metavar=('num','num'), dest='inrange2', nargs='+', required=True,
                            help="first, last event (0 0 for NOP)")

        parser.add_argument("-quiet", dest='quiet',
                            action='store_true', required=False,
                            help="be quieter on database stats")

        parser.add_argument("-res", metavar="num", dest='result', required=False,
                            help="result number (0 for help)")

#        parser.add_argument("-pcases", metavar="file.png", dest='pcases', required=False,
#                            help="dump .png plot of 7 cases")

#        parser.add_argument("-pratio", metavar="file.png", dest='pratio', required=False,
#                            help="dump .png plot of benigh vs. supicious ratio")


        parser.set_defaults(cls=CmdRun)


    def _get_database_(self, indb, quiet):
        db = Database(Config.get_database(indb))
        if not quiet:
            db.print_statistics()
        else:
            db.get_db_stat()
        return db


    def _sanity_check_range_(self, db, inrange, quiet):
        if int(inrange[0]) !=0:
            if int(inrange[0])<int(db.stat[MIN_ID]):
                print("sanity check:", inrange[0],"min db event is lower than first range event",db.stat[MIN_ID])
                exit(1)

        if int(inrange[1]) !=0:
            if int(db.stat[MAX_ID])<int(inrange[1]):
                print("sanity check:", inrange[0],"max db event",db.stat[MAX_ID], "is smaller than max range", inrange[1])
                exit(1)

        if not quiet:
            print("processing", inrange[0], "-", inrange[1])

        return True

        # # if no range passed use min/max event of database
        # if not inrange:
        #     fromid1 = int(db.stat[MIN_ID])
        #     toid1   = int(db.stat[MAX_ID])
        # else:
        #     fromid1 = int(inrange[0])
        #     toid1   = int(inrange[1])
        #
        # if not quiet:
        #     print("processing", fromid1, "-", toid1)
        #     print("")
        #
        # return (inrange[0], inrange[1])


    def run(self, indb1=None,    indb2=None,
               inrange1=None, inrange2=None,
            result=None, quiet=False,
            inmodel=None,
            pcases=None, pratio=None,
            **kwargs):

#        print(len(indb1), indb1)
#        print(len(indb2), indb2)
#        print(len(inrange1), inrange1)
#        print(len(inrange2), inrange2)

        if len(inrange1) % 2 ==1: print("error: invalid range1"); exit(1)
        if len(inrange2) % 2 ==1: print("error: invalid range2"); exit(1)
        if len(inrange1) != len(inrange2):
            print("error: ranges of different length not supported (yet)"); exit(1)

        host1 = indb1[1]
        host2 = indb2[1]
        db1 = self._get_database_(indb1[0], quiet)
        db2 = self._get_database_(indb2[0], quiet)


        dr1 = DatabaseReader4(db1, host1)
        dr2 = DatabaseReader4(db2, host2)

        m1temp = getmodel4(inmodel)
                        # hostid,   name
        model1 = m1temp(str(host1), str(indb1[0]), [11,149], dr1)
        m2temp = getmodel4(inmodel)
        model2 = m2temp(str(host2), str(indb2[0]), [14,36],  dr2)

        model1.set_other(model2)
        model2.set_other(model1)

        if result and int(result)==0:  # just print help and early exit
            model1.print_result(result)
            exit(0)


        run = RunSQL4(dr1, dr2, quiet)

        while len(inrange1)>0:
            range1= [inrange1.pop(0), inrange1.pop(0)]
            range2= [inrange2.pop(0), inrange2.pop(0)]

            self._sanity_check_range_(db1, range1, quiet)
            self._sanity_check_range_(db2, range2, quiet)

            run.run_events(model1, model2,
                           [ int(range1[0]), int(range1[1]) ],
                           [ int(range2[0]), int(range2[1]) ] )


        if result:
            print("\n  ", indb1[1], "===>", model1.hostname + ":")
            model1.print_result(result)

            print("\n  ", indb2[1], "===>", model2.hostname + ":")
            model2.print_result(result)

#        if pcases is not None:
#            pass
#            Plotme.plot_to_png(
#                [model1,model2],
#                [model1.hostnameid,model2.hostnameid],
#                "^c", pcases)

#        if pratio is not None:
#            pass
#            Plotme.plot_to_png(
#                [model1,model2],
#                [model1.hostnameid,model2.hostnameid],
#                "^percent", pratio)
