from cybertrap.dbconst import *
from cybertrap.filter import Filter
from cybertrap.row4 import row2dict
from cybertrap.database import Database
from cybertrap.database_reader4 import DatabaseReader4

import time
from pprint import pprint

# from util.conv import dt_clear_hour, dt_approx_by_delta
from r4.model_cmp4 import ModelCmp4
from r4.modeltemplate import ModelTemplate
from r4.modelconst import RELTIME
from util.conv import printNiceTimeDelta


class RunSQL4:
    def __init__(self, dr1, dr2, quiet=False):
        self.dr1 = dr1
        self.dr2 = dr2


                                     # in generic case is a ModelTemplate
    def run_events(self, model1, model2: ModelCmp4,
                     inrange1, inrange2: list,
                     quiet=False):

        fromid1 = inrange1[0]
        toid1 =   inrange1[1]
        fromid2 = inrange2[0]
        toid2 =   inrange2[1]

        if not quiet:
            lfrom = max( len(str(fromid1)), len(str(fromid2)))
            lto   = max( len(str(  toid1)), len(str(  toid2)))
            print("processing in DB1:", str(fromid1).rjust(lfrom), "-", str(toid1).rjust(lto),
                  "- with model", model1.get_modelname())
            print("processing in DB2:", str(fromid2).rjust(lfrom), "-", str(toid2).rjust(lto),
                  "- with model", model2.get_modelname())
            print("")


        time_start = time.time()

        # send query to databases
        resprox1 = self.dr1.read_sql(str(fromid1), str(toid1))
        if not quiet:
            print("after SELECT1: ", resprox1.rowcount, "events", "("+str(int(resprox1.rowcount/ (time.time()-time_start))), "events/s)")

        resprox2 = self.dr2.read_sql(str(fromid2), str(toid2))
        if not quiet:
            print("after SELECT2: ", resprox2.rowcount, "events", "("+str(int(resprox2.rowcount/ (time.time()-time_start))), "events/s)")


        # event streams counters
        events_processed1 = 0
        events_processed2 = 0

        # luckily Postgres reports number of result rows
        events_total1 = int(resprox1.rowcount)
        events_total2 = int(resprox2.rowcount)
        ev1rjust = len(str(events_total1))
        ev2rjust = len(str(events_total2))
        if not quiet:
            print(str(events_total1+events_total2), "total events to process")
            print("")


        if events_total1>0:
            ev1 = row2dict(resprox1.fetchone())
            model1.to_relative_time(ev1)
        else:
            ev1 = None

        if events_total2>0:
            ev2 = row2dict(resprox2.fetchone())
            model2.to_relative_time(ev2)
        else:
            ev2 = None

        # FIXME: actually when may this be legal?
        if (ev1==None) and (ev2==None):
            print("BUG? no results from db1 AND db2 stream?"); exit(1)


        # find stream with lowest starttime
        # if ev1:
        #     timenow = ev1[RELTIME]
        # if ev2:
        #     if not ev1:
        #         timenow = ev2[RELTIME]
        #     else:
        #         if ev2[RELTIME] < timenow:
        #             timenow = ev2[RELTIME]


        time_start = time.time()

        while True:
#            if (events_processed1+events_processed2) % 40000 == 0:
#                print("count ", str(events_processed1).rjust(ev1rjust), printNiceTimeDelta(ev1[RELTIME]), "",
#                                str(events_processed2).rjust(ev2rjust), printNiceTimeDelta(ev2[RELTIME]) )

            # all events exhausted
            if events_processed1 == events_total1 and \
                events_processed2 == events_total2:
                break

            # db1 finished, so do one from db2
            if events_processed1 == events_total1:
#                timenow = ev2[RELTIME]
                model2.consume_event(ev2)
                events_processed2 +=1
                if events_processed2 < events_total2:
                    ev2 = row2dict(resprox2.fetchone())
                    model2.to_relative_time(ev2)
                continue

            # db2 finished, so do one from db1
            if events_processed2 == events_total2:
#                timenow = ev1[RELTIME]
                model1.consume_event(ev1)
                events_processed1 +=1
                if events_processed1 < events_total1:
                    ev1 = row2dict(resprox1.fetchone())
                    model1.to_relative_time(ev1)
                continue

            if ev1[RELTIME] <= ev2[RELTIME]:
#                timenow = ev1[RELTIME]
                model1.consume_event(ev1)
                events_processed1 +=1
                if events_processed1 < events_total1:
                    ev1 = row2dict(resprox1.fetchone())
                    model1.to_relative_time(ev1)
            else:
#                timenow = ev2[RELTIME]
                model2.consume_event(ev2)
                events_processed2 +=1
                if events_processed2 < events_total2:
                    ev2 = row2dict(resprox2.fetchone())
                    model2.to_relative_time(ev2)

        if not quiet:
            print("")
            print("...last DB1:", ev1[ID], printNiceTimeDelta(ev1[RELTIME]), "@", ev1[TIME])
            print("...last DB2:", ev2[ID], printNiceTimeDelta(ev2[RELTIME]), "@", ev2[TIME])
            processed = events_processed1+events_processed2
            print("-->", processed, "events", "("+str(int(processed/ (time.time()-time_start))), "events/s)")
