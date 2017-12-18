from cybertrap.database import Database

import pandas as pd
from pandas import DataFrame
from pprint import pprint
from sys import exit

class DatabaseReader4:
    def __init__(self, db: Database, host:str):
        self.db = db
        self.host = host


    def read_sql_events(self, event_from: str, event_to: str):
        resprox = self.db.conn.execute(
            "SELECT * FROM events"+
            " LEFT OUTER JOIN file_events USING (id)" +
            " LEFT OUTER JOIN process_events USING (id)" +
            " LEFT OUTER JOIN registry_events USING (id)" +
            " LEFT OUTER JOIN network_events USING (id)" +
            " LEFT OUTER JOIN thread_events USING (id)" +
            " WHERE events.id>="+str(event_from) +
            " AND events.id<="+str(event_to) +
#            " AND (events.type_id=0 OR events.type_id=4)"+
            " ORDER BY events.id ASC")
        return resprox

    def read_sql_one_event(self, event: str):
        result = self.read_sql_events(event, event)
        return list(result)[0]


    def read_sql(self, event_from: str, event_to: str):

        resprox = self.db.conn.execute(
            "SELECT * FROM ("+
            "  SELECT"+
            "    events.id AS id,"+
            "    events.sequence_id,"+
            "    events."+self.db.hostname_in_events+","+
            "    events.type_id,"+
            "    events.pid,"+

            "    events.process_name,"+
            "    parent.id           AS parent_id,"+
            "    parent.process_name AS parent_process_name,"+

            "    events.time,"+
            "    process_events.domain_name,"+
            "    process_events.user_name,"+
            "    process_events.command_line,"+
            "    file_events.type AS fileop, file_events.src_file_name, file_events.dst_file_name,"+

            "    registry_events.type_string, registry_events.path, registry_events.key, registry_events.data"+
#            "    network_events.is_connection_outgoing, network_events.protocol_id,"+
#            "    network_events.local_ip_address, network_events.local_port, network_events.remote_ip_address, network_events.remote_port"+

            "  FROM events"+
            "    LEFT OUTER JOIN process_events USING (id)"+
            "    LEFT OUTER JOIN file_events USING (id)"+
            "    LEFT OUTER JOIN registry_events USING (id)" +
#            "   LEFT OUTER JOIN network_events USING (id)" +
#            "   LEFT OUTER JOIN thread_events USING (id)" +
            "    LEFT OUTER JOIN events AS parent ON events.parent_id = parent.id"+
            "  WHERE events.type_id = 0"+      # process events

            "    AND events.id>="+str(event_from) +
            "    AND events.id<="+str(event_to) +
            "    AND events."+self.db.hostname_in_events+" =" + str(self.host) +

            "  UNION ALL"+


            "  SELECT"+
            "    events.id AS id,"+
            "    events.sequence_id,"+
            "    events."+self.db.hostname_in_events+","+
            "    events.type_id,"+
            "    events.pid,"+

            "    events.process_name,"+
            "    parent.id                 AS parent_id,"+
            "    grant_parent.process_name AS parent_process_name,"+

            "    events.time,"+
            "    process_events.domain_name,"+
            "    process_events.user_name,"+
            "    process_events.command_line,"+
            "    file_events.type AS fileop, file_events.src_file_name, file_events.dst_file_name,"+

            "    registry_events.type_string, registry_events.path, registry_events.key, registry_events.data"+
#            "    network_events.is_connection_outgoing, network_events.protocol_id,"+
#            "    network_events.local_ip_address, network_events.local_port, network_events.remote_ip_address, network_events.remote_port"+

            "  FROM events"+
            "    LEFT OUTER JOIN process_events USING (id)"+
            "    LEFT OUTER JOIN file_events USING (id)"+
            "   LEFT OUTER JOIN registry_events USING (id)" +
#            "   LEFT OUTER JOIN network_events USING (id)" +
#            "   LEFT OUTER JOIN thread_events USING (id)" +
            "    LEFT OUTER JOIN events AS parent ON events.parent_id = parent.id"+
            "    LEFT OUTER JOIN events AS grant_parent ON parent.parent_id = grant_parent.id"+
            "  WHERE events.type_id!=0 "+     # not process events (!=0),
                                              # or for faster testing only file events (=4)

            "    AND events.id>="+str(event_from) +
            "    AND events.id<="+str(event_to) +
            "    AND events."+self.db.hostname_in_events+" =" + str(self.host) +

            ") AS x"+
            " ORDER BY x.id ASC" )
        return resprox





    def find_reboots(self) -> DataFrame:   #,hostid="hostname_id"
        df = pd.read_sql(
            "SELECT id,"+self.db.hostname_in_events+",time,pid,process_name,sequence_id FROM events WHERE sequence_id=0 AND pid=4 ORDER BY id ASC",  #" AND events.hostnames_id="+hostid
            self.db.engine)
        df.set_index('id', inplace=True)
        return df
