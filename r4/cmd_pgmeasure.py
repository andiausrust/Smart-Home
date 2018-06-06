from pprint import pprint

from cybertrap.database import Database
from cybertrap.database_reader4 import DatabaseReader4
from cybertrap.row4 import row2dict

from r4.cmdtemplate import CommandTemplate
from util.config import Config

import pandas as pd

class CmdPgMeasure(CommandTemplate):
    NAME = 'pgmeasure'
    HELP = 'measure Cybertrap Postgres database'

    @staticmethod
    def add_subparser(subparsers):
        parser = subparsers.add_parser(CmdPgMeasure.NAME,
                                       aliases=['pgm'],
                                       help=CmdPgMeasure.HELP)
        parser.add_argument("-d", metavar="dbalias", dest='indb',
                            required=False,
                            help="database alias")

#        parser.add_argument("-reboots", dest='print_reboots',
#                            action='store_true', required=False,
#                            help="show reboots table")

        parser.set_defaults(cls=CmdPgMeasure)


    def run(self, indb=False, print_reboots=False, sort_by_host=False, **kwargs):
        if not indb:
            print("no database specified"); exit(1)

        db = Config.get_database(indb)

        db = Database(db)
        db.print_statistics()

        print("")


        QUERY = "  SELECT "+ \
                "    events.id AS id,"+ \
                "    events.sequence_id,"+ \
                "    events."+db.hostname_in_events+","+ \
                "    events.type_id,"+ \
                "    events.pid,"+ \
                "    events.process_name,"+ \
                "    parent.id                AS parent_id,"+ \
                "    parent.process_name      AS parent_process_name,"+ \
                "    grandparent.process_name AS grandparent_process_name,"+ \
                "    grandparent.id           AS grandparent_id,"+ \
                "    events.time,"+ \
                "    process_events.domain_name,"+ \
                "    process_events.user_name,"+ \
                "    process_events.command_line,"+ \
                "    file_events.type AS fileop, file_events.src_file_name, file_events.dst_file_name,"+ \
                "    registry_events.type_string, registry_events.path, registry_events.key, registry_events.data,"+ \
                "    network_events.is_connection_outgoing, network_events.protocol_id,"+ \
                "    network_events.local_ip_address, network_events.local_port, network_events.remote_ip_address, network_events.remote_port"+ \
                "  FROM events"+ \
                "    LEFT OUTER JOIN process_events USING (id)"+ \
                "    LEFT OUTER JOIN file_events USING (id)"+ \
                "    LEFT OUTER JOIN registry_events USING (id)" + \
                "   LEFT OUTER JOIN network_events USING (id)" + \
                "    LEFT OUTER JOIN events AS parent      ON events.parent_id = parent.id"+ \
                "    LEFT OUTER JOIN events AS grandparent ON parent.parent_id = grandparent.id"+ \
                "  WHERE events.type_id = 4"+ \
                " LIMIT 5"

        df = pd.read_sql(QUERY, db.engine)
        print("got", len(df), "lines")
        pprint(df)

        print("")
        print("")


        resprox = db.conn.execute(QUERY)
        rows = int(resprox.rowcount)
        print("got", rows, "lines")
        while rows>0:
            line = row2dict(resprox.fetchone())
            pprint(line)
            rows -=1

        print("done")





