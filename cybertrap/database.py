from sqlalchemy.engine import create_engine
from sqlalchemy.inspection import inspect
from sqlalchemy.sql.expression import select, desc, and_
from sqlalchemy.sql.functions import func
from sqlalchemy.sql.schema import MetaData, Table

from cybertrap.dbconst import *

import pandas as pd
from pandas import DataFrame

from pprint import pprint


class Database:

    def mount_table_from_db(self, tablename):
        return Table(tablename, self.meta, autoload=True, autoload_with=self.engine)

    def __init__(self, db_url):
        self.db_url = db_url
        self.engine = create_engine(self.db_url, echo=False)
        self.meta = MetaData()

        # connect
        self.conn = self.engine.connect()
        self.inspector = inspect(self.engine)
        self.db_all_table_names = self.inspector.get_table_names()

        # as a simple self-test of working SQLalchemy+Postgres,
        # read and parse event_types table
        self.event_types = {}
        self.db_table_event_types = self.mount_table_from_db('event_types')
        res = self.conn.execute(select([self.db_table_event_types]))
        for row in res:
            self.event_types[row.id] = row.type

        # we are always interested in the events table, so mount it immediately
        self.table_events = self.mount_table_from_db('events')
        self.stat = None


        df_ctunits = pd.read_sql("SELECT * FROM ct_units", self.engine)

        if 'machine_key' in df_ctunits:
            self.is2016format = False
            self.is2017format = True
            self.hostname_in_events = 'ct_units_id'
        else:
            self.is2016format = True
            self.is2017format = False
            self.hostname_in_events = 'hostnames_id'

    def shutdown(self):
        self.engine.dispose()
        # help garbage collector?
        self.engine = None
        self.meta = None
        self.conn = None
        self.inspector = None


    def _get_first_last_row_(self, table):
        sel1 = table.select().order_by('id').limit(1)
        first = self.conn.execute(sel1).fetchone()

        sel2 = table.select().order_by(desc('id')).limit(1)
        last = self.conn.execute(sel2).fetchone()

        return (first,last)

    def _count_table_rows_(self, table):
        sel = select([func.count()]).select_from(table)
        return self.conn.execute(sel).scalar()


    def get_db_stat(self) -> dict:
        """
        Get rough statistic overview of current database:
        rows, min_id, max_id, min_time, max_time
        """
        stat = dict()
        stat[ROWS] = self._count_table_rows_(self.table_events)

        res = self._get_first_last_row_(self.table_events)
        stat[MIN_ID]   = res[0].id
        stat[MIN_TIME] = res[0].time
        stat[MAX_ID]   = res[1].id
        stat[MAX_TIME] = res[1].time

        self.stat = stat
        return stat


    def print_statistics(self):
        if self.stat is None:
            self.get_db_stat()

        print('{} events in database'.format(self.stat['rows']))
        print('  first event: {0:>8} {1}'.format(self.stat[MIN_ID], self.stat[MIN_TIME]))
        print('   last event: {0:>8} {1}'.format(self.stat[MAX_ID], self.stat[MAX_TIME]))

        return self.stat


    def get_hostnames(self, count_events=True) -> (DataFrame, dict):
        # get all distinct hostnames
        if self.is2017format:
            df = pd.read_sql("SELECT DISTINCT (ct_units.id), hostname FROM ct_units" +
                             " LEFT OUTER JOIN events ON events.ct_units_id = ct_units.id" +
                             " ORDER BY ct_units.id", self.engine)
        else: # 2016format
            df = pd.read_sql("SELECT DISTINCT (hostnames.id), hostname FROM hostnames" +
                             " LEFT OUTER JOIN events ON events.hostnames_id = hostnames.id" +
                             " ORDER BY hostnames.id", self.engine)

        df = df.set_index('id')
        df['events'] = -1


        # figure out which hostnames are actually used by events
        if self.is2017format:
            df2 = pd.read_sql("SELECT DISTINCT ct_units_id FROM events", self.engine)
            df2.columns=['hostnames_id']
        else: # 2016format
            df2 = pd.read_sql("SELECT DISTINCT hostnames_id FROM events", self.engine)


        if count_events:
            # query number of events for each hostname_id in database
            for name in df2['hostnames_id']:
                events = pd.read_sql(
                    "SELECT COUNT (*) FROM (SELECT * FROM events WHERE "+self.hostname_in_events+"="+str(name)+") AS x",
                    self.engine)
                df.loc[name,'events'] = events['count'][0]

            # drop lines(hosts) with no events in database
            df = df.drop( df[df.events == -1].index )

        # df[id,hostname,events], { id -> {'events'-> , 'hostname'-> } }
        return df, df.transpose().to_dict(orient='dict')


    def get_count_of_host_event(self, hostid:str) -> int:
                events = pd.read_sql(
                    "SELECT COUNT (*) FROM (SELECT * FROM events WHERE "+self.hostname_in_events+"="+str(hostid)+") AS x",
                    self.engine)
                return int(events['count'][0])
