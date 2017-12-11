from pprint import pprint

from cybertrap.database import Database
from cybertrap.dbconst import MAX_ID
from cybertrap.database_reader4 import DatabaseReader4
from util.config import Config


class CmdPgStat:
    NAME = 'pgstat'
    HELP = 'get basic statistics of Cybertrap Postgres database'

    @staticmethod
    def add_subparser(subparsers):
        parser = subparsers.add_parser(CmdPgStat.NAME,
                                       aliases=['pgst'],
                                       help=CmdPgStat.HELP)
        parser.add_argument("-d", metavar="dbalias", dest='db',
                            help="database alias")

        parser.add_argument("-reboots", dest='print_reboots',
                            action='store_true', required=False,
                            help="show reboots table")

        parser.set_defaults(cls=CmdPgStat)


    def run(self, db=False, print_reboots=False, **kwargs):
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
          print("")
          print(reboots)
