from pprint import pprint

from cybertrap.dbconst import PID, PROCESS_NAME, SEQUENCE_ID
from cybertrap.database import Database
from cybertrap.database_reader4 import DatabaseReader4

from r4.cmdtemplate import CommandTemplate
from util.config import Config


class CmdPgStat(CommandTemplate):
    NAME = 'pgstat'
    HELP = 'get basic statistics of Cybertrap Postgres database'

    @staticmethod
    def add_subparser(subparsers):
        parser = subparsers.add_parser(CmdPgStat.NAME,
                                       aliases=['pgst'],
                                       help=CmdPgStat.HELP)
        parser.add_argument("-d", metavar="dbalias", dest='db',
                            required=False,
                            help="database alias")

        parser.add_argument("-reboots", dest='print_reboots',
                            action='store_true', required=False,
                            help="show reboots table")

        parser.add_argument("-sorthost", dest='sort_by_host',     # requested by David :-)
                            action='store_true', required=False,
                            help="sort reboots table by hostid (ct_units_id)")


        parser.set_defaults(cls=CmdPgStat)


    def run(self, db=False, print_reboots=False, sort_by_host=False, **kwargs):

        if not db:
            print("no database specified"); exit(1)

        db = Config.get_database(db)

        db = Database(db)
        db.print_statistics()

        print("")
        hostdf, hostdic = db.get_hostnames(True)
        pprint(hostdf)
#        pprint(hostdic); exit(1)


        if print_reboots:
            dr = DatabaseReader4(db, "")
            reboots = dr.find_reboots()
            reboots.drop([PID, PROCESS_NAME, SEQUENCE_ID],axis=1,inplace=True)

            if sort_by_host:
                reboots.sort_values(['ct_units_id','time'],ascending=[True, True], inplace=True)

            print("")
            print(reboots)
