from cybertrap.dbconst import *
from cybertrap.filter import Filter
from cybertrap.row4 import row2dict
from cybertrap.database import Database
from cybertrap.database_reader4 import DatabaseReader4

import time
import datetime as dt
from pprint import pprint

# from util.conv import dt_clear_hour, dt_approx_by_delta
from r4.model_cmp4b import ModelCmp4b
from r4.modeltemplate import ModelTemplate
from r4.modelconst import RELTIME
from util.conv import printNiceTimeDelta, dt_to_str, parse_datetimestring_to_dt

from util.config import Config


class RunSelf4:
    @staticmethod
    def _get_database_(indb, quiet):
        db = Database(Config.get_database(indb))
        if not quiet:
            db.print_statistics()
        else:
            db.get_db_stat()
        return db


    def __init__(self, db, host, quiet=False):
        self.db = RunSelf4._get_database_(db, quiet)
        self.host = host

        self.dr = DatabaseReader4(self.db, self.host)

        self.min_event = self.dr.find_first_event_for_host().index[0]
        self.max_event = self.dr.find_last_event_for_host().index[0]
        self.quiet = quiet

        if not quiet:
            print("database has events for host", self.host, "in range:")
            ev1 = self.read_sql_one_event_and_convert(self.min_event)
            print("  ", ev1[ID], dt_to_str(ev1[TIME]) )
            ev2 = self.read_sql_one_event_and_convert(self.max_event)
            print("  ", ev2[ID], dt_to_str(ev2[TIME]) )

                                     # hostid    name   colors    dr
        self.model1 = ModelCmp4b( str(host), str(db), [11,149], self.dr, quiet=True, fromreboot=False) # fromreboot=True
        self.model2 = ModelCmp4b( str(host), str(db), [14,36],  self.dr, quiet=True, fromreboot=False) # fromreboot=True

        self.model1.set_other(self.model2)
        self.model2.set_other(self.model1)



    def read_sql_one_event_and_convert(self, eventid:str) -> dict:
        resprox = self.dr.read_sql(eventid, eventid)
        if int(resprox.rowcount)!=1:
            return None
        else:
            event = row2dict(resprox.fetchone())
            Filter.run_filters(event)
            return event

    @staticmethod
    def _convert_start_time_to_event_number_(dr: DatabaseReader4, host, eventid, quiet):
        astime = parse_datetimestring_to_dt(eventid)
        df = dr.find_first_event_on_or_after_time(dt_to_str(astime) )
        if df.size==0:
            print("start_time_to_event_number: HELP! did not find any events after", dt_to_str(astime), "for host", host)
            exit(1)
        if not quiet:
            print("Host", host, "input time:", dt_to_str(astime))
            print("Host", host, "  nearest->", df['time'][0], df.index[0])
        return df.index[0]


    @staticmethod
    def _convert_end_time_to_event_number_(dr: DatabaseReader4, host, eventid, quiet):
        astime = parse_datetimestring_to_dt(eventid)
        df = dr.find_first_event_before_time(dt_to_str(astime) )
        if df.size==0:
            print("end_time_to_event_number: HELP! did not find any events before",dt_to_str(astime), "for host", host)
            exit(1)
        if not quiet:
            print("Host", host, "input time:", dt_to_str(astime))
            print("Host", host, " nearest ->", df['time'][0], df.index[0])
        return df.index[0]

                             # int or str
    def consume_events(self, fromid, toid, dualconsume=False) -> int:
#        print("consume_events:", fromid, "-", toid)

        if type(fromid) is str and (not fromid.isdigit()):
            fromid = self._convert_start_time_to_event_number_(self.dr, self.host, fromid, self.quiet)

        if type(toid) is str and (not toid.isdigit()):
            toid = self._convert_end_time_to_event_number_(  self.dr, self.host, toid, self.quiet)

#        print("consume_events:", fromid, "-", toid)

        fromid = int(fromid)    # if number is in a string
        toid = int(toid)

        if fromid < toid:
            ev = self.dr.read_sql_one_event(str(fromid))
            if not self.quiet:
                print("consume FROM:", str(ev[ID])+" ", dt_to_str(ev[TIME]))
            ev = self.dr.read_sql_one_event(str(toid))
            if not self.quiet:
                print("consume   TO:", str(ev[ID])+" ", dt_to_str(ev[TIME]))

            events_processed = 0
            time_start = time.time()
            resprox = self.dr.read_sql(str(fromid), str(toid))
            if not dualconsume:
                self.model2.ranges_consumed.append( [fromid, toid] )
    #        self.model1.ranges_consumed.append( [fromid, toid] )
            events_total = int(resprox.rowcount)

    #        if not self.quiet:
            timespan = time.time()-time_start
            if not self.quiet:
                print("{:.2f}".format(timespan)+"s: ","SELECT: ", resprox.rowcount, "events", "("+str(int(resprox.rowcount/ timespan)), "events/s)")

            time_start = time.time()
            while events_processed<events_total:
                ev = row2dict(resprox.fetchone())
                self.model2.consume_event(ev)
                if dualconsume:
                    self.model1.consume_event(ev)

                events_processed +=1

    #        if not self.quiet:
            timespan = time.time()-time_start
            if not self.quiet:
                print("{:.2f}".format(timespan)+"s: ", events_processed, "events consumed")

            return events_processed
        else:
            print("BUG? consume_events:", fromid, " is not <", toid, "? - doing nothing")
            return 0


    def consume_reference(self, ranges: list):
        while len(ranges)>0:
            fromid = ranges.pop(0)

            if fromid is tuple:
                self.consume_events(fromid[0], fromid[1], dualconsume=True)
            else:
                toid = ranges.pop(0)
                self.consume_events(fromid,    toid,      dualconsume=True)


    def run_evaluate(self):
        time_start = time.time()
        self.model2.do_evaluation(force=True)
        same_ident, same_sym, same_asym, fuz_ident, fuz_sym, fuz_asym, unique = \
            self.model2.do_count_pair_types()
        timespan = time.time()-time_start

        if not self.quiet:
            print("{:.2f}".format(timespan)+"s:  pair evaluation done -->",
                  "S", len(self.model2.pairs_same),
                  "V", len(self.model2.pairs_var),
                  "  SI", same_ident,
                  " SS", same_sym,
                  " SA", same_asym,
                  "  FI", fuz_ident,
                  " FS", fuz_sym,
                  " FA", fuz_asym,
                  "  UNI", unique)

    # no From was provided, so get a start by substraction
    def substract_from_max_event(self, seconds):
        ev = self.read_sql_one_event_and_convert(self.max_event)
        if not self.quiet:
            print("last event in database:", ev[TIME], ev[ID])
        newtime = ev[TIME] - dt.timedelta(seconds=seconds)
        newtime = newtime.strftime('%Y-%m-%d.%H:%M:%S.%f')
        newstart = self._convert_start_time_to_event_number_(self.dr, self.host, newtime, self.quiet)
        if not self.quiet:
            print(" using as actual start:", newtime, newstart)
        return newstart


    def shutdown(self):
#        ev = self.model2.last_event_consumed
#        print("== SHUTDOWN, last event consumed was:", str(ev[ID])+" ", str(ev[TIME]) )

        self.db.shutdown()
        self.db = None

        self.dr = None

        self.model1.other = None
        self.model2.other = None
        self.model1 = None
        self.model2 = None
