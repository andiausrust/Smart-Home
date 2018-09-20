import datetime as dt
from collections import OrderedDict
from datetime import timedelta
from pprint import pprint

from cybertrap.database_reader4 import DatabaseReader4
from cybertrap.filter import Filter
from cybertrap.row4 import row2dict
from r4.modeltemplate import ModelTemplate
from r4.modelconst import *

from sys import exit
from copy import deepcopy

from cybertrap.dbconst import *
from util.conv import dt_clear_hour, dt_approx_by_delta, dt_to_str, printNiceTimeDelta
from util.rawterm import RawTerm as rt

from nilsimsa import Nilsimsa, compare_digests


# terminal colors
CLIGHTRED = 9
CLIGHTGREEN = 10
CDARKGREEN = 34
COFFGREEN = 121

CDARKRED = 160
CNORM = 15
CDARK = 241
CDARKBLUE = 26

CVIO3 = 141
CVIO2 = 134
CVIO1 = 132

CTURQ = 14
COFFYELLOW = 228

CORANGE = 214


class ModelCmp4b(ModelTemplate):
    def get_modelname(self):
        return "CMP4b"

    def __init__(self, hostid :str,
                     hostname :str,
                       colors :list,
                           dr :DatabaseReader4,
                        **kwargs):

        self.dr = dr
        self.hostid     = hostid
        self.hostname   = hostname
        self.hostnameid = hostname + "/" + hostid

        self.hostcolhi, self.hostcollo = colors

        self.clear_state()  ####### sub-states

        self.last_event_consumed = None

        self.other  = None
        self.ioc = None

        self.reboots = []
        self.rebootid  = None   # event id of last seen reboot as int
        self.rebootstr = None   # as string
        self.time_first_reboot = None   # time of first reboot

        self.fromreboot = True  # default
        if 'fromreboot' in kwargs:
            self.fromreboot = kwargs['fromreboot']

        self.quiet = False
        if 'quiet' in kwargs:
            self.quiet = kwargs['quiet']

        self.tick_start = None
        self.tick_end   = None
        self.tick_delta = timedelta(seconds=60) *30   # 60*3    # ticker for model internal periodic tasks

        self.ranges_consumed = []

        self.addnetwork = False       # network events analysis
        if 'addnetwork' in kwargs:
            self.addnetwork = kwargs['addnetwork']

        self.addfileop = False        # detailes file operations
        if 'addfileop' in kwargs:
            self.addfileop = kwargs['addfileop']

        self.allfiles = False          # dump all files accessed, not only the first one
        if 'allfiles' in kwargs:
            self.allfiles = kwargs['allfiles']

        self.processonly = False       # show only process events in details listing
        if 'processonly' in kwargs:
            self.processonly = kwargs['processonly']

    def create_deepcopy(self):
        m = ModelCmp4b( self.hostid, self.hostname, [self.hostcolhi, self.hostcollo],  self.dr)

        m.pairs_same = deepcopy(self.pairs_same)
        m.pairs_var =  deepcopy(self.pairs_var)

        m.last_event_consumed = deepcopy(self.last_event_consumed)
        m.reboots = deepcopy(self.reboots)
        m.rebootid = deepcopy(self.rebootid)
        m.rebootstr = deepcopy(self.rebootid)
        m.time_first_reboot = deepcopy(self.time_first_reboot)
        m.tick_start = deepcopy(self.tick_start)
        m.tick_end = deepcopy(self.tick_end)
        m.tick_delta = deepcopy(self.tick_delta)
        m.ranges_consumed = deepcopy(self.ranges_consumed)

        m.total_events = deepcopy(self.total_events)
        m.total_events_file     = deepcopy(self.total_events_file)
        m.total_events_network  = deepcopy(self.total_events_network)
        m.total_events_process  = deepcopy(self.total_events_process)
        m.total_events_registry = deepcopy(self.total_events_registry)
        m.total_events_thread   = deepcopy(self.total_events_thread)

        m.result = deepcopy(self.result)

        m.quiet       = deepcopy(self.quiet)
        m.fromreboot  = deepcopy(self.fromreboot)
        m.addnetwork  = deepcopy(self.addnetwork)
        m.addfileop   = deepcopy(self.addfileop)
        m.allfiles    = deepcopy(self.allfiles)
        m.processonly = deepcopy(self.processonly)

        return m


    def set_other(self, othermodel):
        if othermodel == self:
            print("bug? cannot compare with myself")
            exit(1)
        self.other = othermodel

    def clear_state(self):
        # global state
        self.pairs_same = {}
        self.pairs_var  = {}

        self.total_events          = 0    # start with zero maybe a problem if
                                          # used to calculate percentage of total events
        self.total_events_file     = 0
        self.total_events_network  = 0
        self.total_events_process  = 0
        self.total_events_registry = 0
        self.total_events_thread   = 0

        # history of states
        self.result = OrderedDict()
#        self.result_window = None    # int


    def do_count_pair_types(self) -> ():
        same_ident = 0
        same_sym   = 0
        same_asym  = 0
        fuz_ident = 0
        fuz_sym   = 0
        fuz_asym  = 0
        unique   = 0
        whatelse = 0

        for looppair in self.pairs_same:
            pair = self.pairs_same[looppair]
            if pair[EVAL_TYPE] == TSAME_IDENT:
                same_ident +=1
            elif pair[EVAL_TYPE] == TSAME_SYM:
                same_sym +=1
            elif pair[EVAL_TYPE] == TSAME_ASYM:
                same_asym +=1
            else:
                print("bug? what same type is this?", pair[PAIR][0],"==>",pair[PAIR][1], " ", pair[LAST_EVENT], pair[EVAL_EVENT], pair[EVAL_TYPE])
                whatelse += 1

        for looppair in self.pairs_var:
            pair = self.pairs_var[looppair]
            if pair[EVAL_TYPE] == TFUZ_IDENT:
                fuz_ident +=1
            elif pair[EVAL_TYPE] == TFUZ_SYM:
                fuz_sym +=1
            elif pair[EVAL_TYPE] == TFUZ_ASYM:
                fuz_asym +=1
            elif pair[EVAL_TYPE] == TUNIQUE:
                unique +=1
            else:
                print("bug? what var type is this?", pair[PAIR][0],"==>",pair[PAIR][1], " ", pair[LAST_EVENT], pair[EVAL_EVENT], pair[EVAL_TYPE])
                whatelse += 1

        return (same_ident, same_sym, same_asym, fuz_ident, fuz_sym, fuz_asym, unique)

    def get_uniqueness_state(self, timetick: dt.datetime) -> dict:
        same_ident, same_sym, same_asym, \
        fuz_ident,   fuz_sym,  fuz_asym, \
        unique = self.do_count_pair_types()

        result = dict()

        result['c1_same_ident'] = same_ident
        result['c2_same_sim']   = same_sym
        result['c3_same_asym']  = same_asym

        result['c4_fuz_ident'] = fuz_ident
        result['c5_fuz_sim']   = fuz_sym
        result['c6_fuz_asym']  = fuz_asym
        result['c7_uniq']    =  unique

        result['abs_same'] = len(self.pairs_same)
        result['abs_fuz']  = len(self.pairs_var)
        all = len(self.pairs_same)+len(self.pairs_var)
        result['abs_all'] = all

        result['percent_100%'] = 1.0
        if all>0:
            result['percent_ok' ]  = (same_ident+same_sym + fuz_ident+fuz_sym) / all
            result['percent_inspect' ] = (same_asym+fuz_asym+unique) / all
        else:     # if we're rarely unlucky and no pairs found yet
            result['percent_ok' ]  = 0
            result['percent_inspect' ] = 0


        result['i3_same_asym'] = same_asym
        result['i6_fuz_asym']  = fuz_asym
        result['i7_uniq']      = unique
        result['i_all']        = all

        return result



    def get_state(self, timetick: dt.datetime):
        result = dict()

        result['total_events_file']     = self.total_events_file
        result['total_events_process']  = self.total_events_process
#        result['total_events_network']  = self.total_events_network
#        result['total_events_thread']   = self.total_events_thread
#        result['total_events_registry'] = self.total_events_registry
        result['total_sum_events']      = self.total_events

        if self.other:
            result.update(self.get_uniqueness_state(timetick))

        return result



    def save_state(self, timetick: dt.datetime):
        self.result[timetick] = self.get_state(timetick)
        pass

##############################################################################


    def to_relative_time(self, ev: dict):
        if self.time_first_reboot:
            ev[RELTIME] = ev[TIME]-self.time_first_reboot
        else:
            ev[RELTIME] = ev[TIME]-ev[TIME]

    def set_reboot(self, row):
        self.rebootid =  int(row[ID])
        self.rebootstr = row[ID]

        if not self.quiet:
            if not self.fromreboot and not self.last_event_consumed:
                print(rt.setfg(CLIGHTRED), "FORCED"+
                      rt.setfg(self.hostcolhi),
                     "REBOOT at ",row[ID], self.hostnameid, "  ", row[TIME], rt.resetfg())
            else:
                print(rt.setfg(self.hostcolhi),
                    "  REBOOT at ",row[ID], self.hostnameid, "  ", row[TIME], rt.resetfg())


        self.reboots.append(self.rebootid)

        # first reboot? need to remember time
        if not self.time_first_reboot:
            self.time_first_reboot = row[TIME]

        if self.tick_start is None:
            # find ourselves a nice start with a zeroed hour so graphing is prettier
            start_event_time        = row[TIME]
            start_event_time_zeroed = dt_clear_hour(start_event_time)

            self.tick_start = dt_approx_by_delta(start_event_time_zeroed, start_event_time, self.tick_delta)
            self.tick_end = self.tick_start + self.tick_delta
    #        print(self.tick_start)
    #        print(self.tick_end)
        else:
            pass
#            print(self.hostid, "IGNORED at",row[ID])
#            self.tick_start = None

##############################################################################

    @staticmethod
    def _path_to_fragments_with_file(path:str) -> list:
        return path.split('\\')[1:]

    @staticmethod
    def _path_to_fragments_without_file(path:str) -> list:
        return path.split('\\')[1:-1]


    @staticmethod
    def _add_one_to_key_(thisdict, key):
        if key in thisdict:
            thisdict[key] +=1
        else:
            thisdict[key] = 1

    @staticmethod
    def _nilsimsa_distance_(indigest1, indigest2: Nilsimsa):
        return (128-compare_digests(indigest1.hexdigest(), indigest2.hexdigest()))

##############################################################################

    def consume_process(self, ev):
        evid        = int(ev[ID])
        timestamp   = ev[TIME]
        binary      = ev[PROCESS_NAME]

        cmd_line          = ev[COMMAND_LINE]
        user_name         = ev[USER_NAME]
        domain_name       = ev[DOMAIN_NAME]
#       working_directory = ev[WORKING_DIRECTORY]   # ignore for now

        parent_binary = ev[PARENT_PROCESS_NAME]
        parent_id     = ev[PARENT_ID]

        grandparent_binary = ev[GRANDPARENT_PROCESS_NAME]
        grandparent_id     = ev[GRANDPARENT_ID]

        if grandparent_id is None:
            if parent_id is None:
                grandparent_binary = r"\REBOOT"
            else:
                grandparent_binary = r"\REBOOT"
        else:
            grandparent_id     = int(ev[GRANDPARENT_ID])


        if parent_id is None:
            # print("P", evid, "parent is None, so I must be the reboot process event")
            # so parent_id==None, too
            parent_binary = r"\REBOOT"

            if int(ev[ID]) != self.rebootid:
                print("BUG in data?", evid, "event parent is None") #, but my last rebootid is", self.rebootid)
        else:
            parent_id = int(parent_id)

        # I have parent information (=I'm not the reboot event)
        if parent_binary is not None:
            # so we can build a pair relation
            relation = (parent_binary,binary)

            item = None
            if relation in self.pairs_same:
                # a same pair again
                item = self.pairs_same[relation]
            elif relation in self.pairs_var:
                # I have seen this pair before
                item = self.pairs_var[relation]

            if parent_id is None:  # we have no parent, so surely also no grandparent info
                parent_id = 0
                grandp_id = 0
                gpppair = None

            else:  # find our grandparent
                if grandparent_id and item:
                    grandp_id = grandparent_id
                    gpprelation = (grandparent_binary, parent_binary)
                    if gpprelation in self.pairs_same:
                        gpppair = self.pairs_same[gpprelation]
                    elif gpprelation in self.pairs_var:
                        gpppair = self.pairs_var[gpprelation]
                    else:
                        gpppair = None
                        grandp_id = 0
                        if self.fromreboot:
                            print("BUG? cannot find grandparent pair for:")
                            print("", grandparent_id, grandparent_binary)
                            print("", parent_id, parent_binary)
                            print("", evid, binary)
                            exit(1)
                else:
                    grandp_id = 0
                    gpppair = None


            if item:
                item[EXECS].append( (grandp_id,parent_id,evid,timestamp) )
                item[LAST_TIME] = timestamp
                item[LAST_EVENT] = evid
            else:
                # new to me, so instantiate a new entry
                item = self.instantiate_pair(relation,evid,timestamp,parent_id, grandp_id)
                self.save_pair_dict(relation, item, evid, timestamp, grandparent_binary)

            if grandp_id != 0:
                if gpppair[PAIR] not in item[PARENT_PAIR]:
                    item[PARENT_PAIR][gpppair[PAIR]] =     [ (gpppair, grandp_id,parent_id) ]
                else:
                    item[PARENT_PAIR][gpppair[PAIR]].append( (gpppair, grandp_id,parent_id) )

        else:
#            pass
            print(evid, binary, " has no parent :-(")


    # def _find_execution_of_binary_(self, evid, binary, inpairs):
    #     parentpair = None
    #     for looppair in inpairs:
    #         pair = inpairs[looppair]
    #
    #         if pair[PAIR][1]==binary:
    #             if pair[FIRST_EVENT] <= evid and \
    #                evid <= pair[LAST_EVENT]:
    #                     for entry in pair[EXECS]:
    #                        if entry[2]==evid:
    #                            parentpair = (pair, entry)
    #                            break
    #     return parentpair
    #
    #
    # def find_parent_pair(self, parent_id, child_binary):
    #     parentpair = self._find_execution_of_binary_(parent_id, child_binary, self.pairs_same)
    #     if not parentpair:
    #         parentpair = self._find_execution_of_binary_(parent_id, child_binary, self.pairs_var)
    #     return parentpair


    def instantiate_pair(self, relation:tuple, evid:int, timestamp, parent_id:int, grandp_id:int):
        item = {}
        item[PAIR] = relation

        item[PAR_FRAG] = self._path_to_fragments_with_file(relation[0])
        item[PAR_FRAG_CUT] = item[PAR_FRAG][:-1]
        item[PAR_TUPL] = tuple(map(len,item[PAR_FRAG]))
        item[PAR_TUPL_CUT] = item[PAR_TUPL][:-1]

        item[BIN_FRAG] = self._path_to_fragments_with_file(relation[1])
        item[BIN_FRAG_CUT] = item[BIN_FRAG][:-1]
        item[BIN_TUPL] = tuple(map(len,item[BIN_FRAG]))
        item[BIN_TUPL_CUT] = item[BIN_TUPL][:-1]

        item[MYDIR_PRENIL] = {}
        item[MYDIR_PREFIX] = {}
#        item[MYDIR_TUPL] = {}

        item[EXECS] = [(grandp_id, parent_id, evid, timestamp)]
        item[FIRST_EVENT] = evid
        item[FIRST_TIME]  = timestamp
        item[LAST_EVENT]  = evid
        item[LAST_TIME]   = timestamp
        item[PARENT_PAIR] = {}

        item[FRIEND] = None
        item[EVAL_EVENT] = None
        item[EVAL_TYPE]  = TUNIQUE
        item[EVAL_STATE] = None

        return item


    def force_late_same_to_var_promotion(self):
        if self.other:
            topromote = []

            # search for same matches in var array
            for looppair in self.pairs_var:
                if looppair in self.other.pairs_var:
                    topromote.append(looppair)

            # promote myself and other match to sameness forever
            for relation in topromote:
                item = self.pairs_var.pop(relation)
                item[EVAL_EVENT] = None
                item[EVAL_TYPE] = None
                item[EVAL_STATE] = None
                self.pairs_same[relation] = item

                item_other = self.other.pairs_var.pop(relation)
                item_other[EVAL_EVENT] = None
                item_other[EVAL_TYPE] = None
                item_other[EVAL_STATE] = None
                self.other.pairs_same[relation] = item_other

                item[FRIEND]       = item_other
                item_other[FRIEND] = item


    def save_pair_dict(self, relation, item, evid, timestamp, gpbinary):
            # insert pair data structure into active sets
            # called either a) for brand new pair or b) for resurrection of expired pair

            if self.other and relation in self.other.pairs_var:
                # new to us, but other has seen this pair already,
                # so we are actually same
                self.pairs_same[relation] = item

                # promote on other side to same-ness
                item_other = self.other.pairs_var.pop(relation)
                # and needs to be re-evaluated
                item_other[EVAL_EVENT] = None
                item_other[EVAL_TYPE] = None
                item_other[EVAL_STATE] = None
                self.other.pairs_same[relation] = item_other

#                 here_friend = item_other[FRIEND]
#                 if here_friend is not None:
#                     # if other had a friend here already, it must be a fuzzy matched friend
#                     # we have to divorce them, as same-ness is better
#                     print("FIXME! BUG! var has friend!")
#                     exit(1)

                # forge a stable bond as same friends forever
                item[FRIEND]       = item_other
                item_other[FRIEND] = item

                grandparent = ""
                if gpbinary:
                    grandparent = gpbinary  #[PAIR][0]
#                    print( rt.setfg(CDARK), item[PARENT_PAIR][PAIR][0], rt.resetfg(), " ===> ",
#                           rt.setfg(CDARK), item[PARENT_PAIR][PAIR][1], rt.resetfg() )

                exec = item[EXECS][-1]
                if not self.quiet:
                    print(rt.setfg(self.hostcollo), str(len(self.pairs_same)).rjust(2), str(len(self.pairs_var)).rjust(2),
                          rt.setfg(CDARK), " -:", self.hostid, str(exec[2]), timestamp,
                          rt.setfg(CDARKBLUE), grandparent+"("+str(exec[0])+")", rt.resetfg(), "===>",
                          rt.setfg(CNORM), relation[0]+"("+str(exec[1])+")", rt.resetfg(), "===>",
                          rt.setfg(CNORM), relation[1], rt.resetfg())

            else:
                grandparent = ""
                if gpbinary:
                    grandparent = gpbinary   #[PAIR][0]

#                if item[PARENT_PAIR]:
#                    print( rt.setfg(CDARK), item[PARENT_PAIR][PAIR][0], rt.resetfg(), " ===> ",
#                           rt.setfg(CDARK), item[PARENT_PAIR][PAIR][1], rt.resetfg() )

                # new to us and also unknown to other
                # so just save, until we have some additional events to find a friend,
                self.pairs_var[relation] = item
                exec = item[EXECS][-1]
                if not self.quiet:
                    print(rt.setfg(self.hostcolhi), str(len(self.pairs_same)).rjust(2), str(len(self.pairs_var)).rjust(2),
                          rt.setfg(CNORM), "+ :", self.hostid, str(exec[2]), timestamp,
                          rt.setfg(CDARKBLUE), grandparent+"("+str(exec[0])+")", rt.resetfg(), "===>",
                          rt.setfg(CNORM), relation[0]+"("+str(exec[1])+")", rt.resetfg(), "===>",
                          rt.setfg(CNORM), relation[1], rt.resetfg())

##############################################################################

    @staticmethod
#                              frags_cut
    def add_prefix(store:dict, prefix: list):
        intuple = tuple(prefix)

        lastfound = {}
        testfound = {}
        testlen = 1

        while True:
            for testtuple in store:
                if testlen<=len(testtuple):
                    if testtuple[:testlen]==intuple[:testlen]:
                        # a known prefix
                        testfound[testtuple]=store[testtuple]

    #        print("len", str(testlen), "found", len(testfound))
            if len(testfound)==0:
                    # in this round no matches, so the -1 shorter one must be solution
                    testlen -= 1
                    break
            else:
                # try again with longer prefix
                testlen+=1
                lastfound = testfound
                testfound = {}

    #    print("do at", str(testlen), "with", len(lastfound))
        if testlen==0:    # at pos 1 different, so must be new entry
            if intuple in store:
                store[intuple][()] += 1     # must be case / -> ()
            else:
                store[intuple] = {():1}     # /bla/foo -> () = 1
        else:
    #        print("  merging:")
    #        for thisone in sorted(lastfound):
    #            print("     ",thisone)
            temp = {}
            for todelete in lastfound:
                temp[todelete] = store.pop(todelete)

            # make entry
            newindex = intuple[:testlen]
            temptuple = tuple(map(len,intuple[testlen:]))
            store[newindex] = { temptuple : 1}

            # loop over saved entries
            for cutme in temp:
                pretuple = cutme[:testlen]                    # cut down cleartext prefix
                posttuple = tuple(map(len,cutme[testlen:]))   # rest turns to anonymous len
    #            print(" pre:", pretuple, "  post:",posttuple)

                if pretuple in store:       # must exist because of new entry
                    existingdata = store[pretuple]

                    for datatuple in temp[cutme]:
                        oldcount = temp[cutme][datatuple]
                        newtuple = posttuple+datatuple        # new number tuple in front
                        if newtuple in existingdata:
                            existingdata[newtuple] += oldcount
                        else:
                            existingdata[newtuple]  = oldcount
                else:
                    print("Bug? cannot find ", pretuple)


    def _get_process_from_database(self, eventid:str) -> dict:
        # go to database fetch process event
        resprox = self.dr.read_sql(eventid, eventid)
        if int(resprox.rowcount)!=1:
            print("BUG! queried for process event",eventid, "but instead got",resprox.rowcount, "events?")
            exit(1)

        procevent = row2dict(resprox.fetchone())
        Filter.run_filters(procevent)
        self.to_relative_time(procevent)

        return procevent

    @staticmethod
    def _preprocess_file_for_special_dirs(pair, src_file, fileop):
            t1_frags_without_file = ModelCmp4b._path_to_fragments_without_file(src_file)

#            t1 = tuple(map(len,t1_frags_without_file))
#            print(src_file, "", t1_frags_without_file, "", t1)
            l = len(pair[BIN_TUPL_CUT])
            if t1_frags_without_file[:l] == pair[BIN_FRAG_CUT]:   # if t1[:l]== binentry[BIN_TUPL_CUT]:
                t1_frags_without_file = ["EXEDIR"]+t1_frags_without_file[l:]
#                t1 = (-99,)+t1[l:]

            # access in root, so rise by one virtual ROOT directory
            if len(t1_frags_without_file)==0:
#                print("S", src_file, evid)
                filename = ModelCmp4b._path_to_fragments_with_file(src_file)
                if len(filename)==0:
                    print("BUG in file event? ROOT access expected but got:",src_file)
#                    print("frags_without_file:", t1_frags_without_file)
#                    print("frags_with_file:", filename)
                #filename = ModelCmp4b._path_to_fragments_with_file(src_file)[-1]
                t1_frags_without_file = ["ROOT"]
#                t1 = (-90,len(filename))

#            print(src_file, "", t1_frags_without_file, "", t1)

            if fileop:
                t1_frags_without_file[0] = FILEOP2RW[fileop] + t1_frags_without_file[0]
            return t1_frags_without_file

    @staticmethod
    def _ip_to_path_with_class(ip_address:str):
        splitip = ip_address.split('.')
        prefix = 'NETG'

        if splitip[0]=='10':                            # 10.*.*.*
            prefix = 'NETL'
        elif splitip[0]=='192' and splitip[1]=='168':   # 192.168.*.*
            prefix = 'NETL'
        elif splitip[0]=='172':                         # 172.16.*.* -- 172.31.*.*
            secondip = int(splitip[1])
            if secondip>=16 and secondip<=31:
                prefix = 'NETL'
        elif splitip[0]=='127':                         # 127.*.*.*
            prefix = 'NETH'

        splitip.insert(0,prefix)

        return splitip


    def consume_network(self, ev):
        evid          = int(ev[ID])
        timestamp     = ev[TIME]
        binary        = ev[PROCESS_NAME]
        parent_binary = ev[GRANDPARENT_PROCESS_NAME]

        if parent_binary is not None:
            relation = (parent_binary, binary)

            item = self.pairs_same.get(relation)

            if not item:
                 item = self.pairs_var.get(relation)

            if not item:        # network event with no existing process pair
                item = self._create_process_container_on_the_fly(ev)


            remote_address = ev[REMOTE_IP_ADDRESS]
            # PORT = str(ev[REMOTE_PORT])

            splitip = ModelCmp4b._ip_to_path_with_class(remote_address)
            self.add_prefix(item[MYDIR_PREFIX], splitip)

            item[LAST_EVENT]  = evid
            item[LAST_TIME]   = timestamp


    # so instantiate an empty process container on the fly
    def _create_process_container_on_the_fly(self, ev):
        evid          = int(ev[ID])
        timestamp     = ev[TIME]
        binary        = ev[PROCESS_NAME]
        parent_binary = ev[GRANDPARENT_PROCESS_NAME]

        relation = (parent_binary, binary)

        parent_id          = int(ev[PARENT_ID])
        grandparent_id     = int(ev[GRANDPARENT_ID])

        # go to database fetch process event
        procevent = self._get_process_from_database(ev[PARENT_ID])

        if procevent[ID] != ev[PARENT_ID] or \
           procevent[PARENT_ID] != ev[GRANDPARENT_ID]:
           print("BUG!", evid, "proc event mismatches file event parent!")
           print("expected:",   ev[GRANDPARENT_ID], ev[PARENT_ID])
           print("     got:", procevent[PARENT_ID], procevent[ID] )
           exit(1)

        item = self.instantiate_pair(relation,parent_id,timestamp, grandparent_id,   procevent[GRANDPARENT_ID])
        self.save_pair_dict(relation,   item, parent_id,timestamp,                   procevent[GRANDPARENT_PROCESS_NAME])

        return item


    def consume_file(self, ev):
        evid          = int(ev[ID])
        timestamp     = ev[TIME]
        binary        = ev[PROCESS_NAME]
        parent_binary = ev[GRANDPARENT_PROCESS_NAME]

        fileop   = ev[TYPE]
        src_file = ev[SRC_FILE_NAME]

        process_evid = ev[PARENT_ID]   # parent of file event is the process event == the process

        if process_evid == self.rebootstr:   # pointing to reboot event
            if ev[PID]!=4:  # bug, event was reparented to PID 4
                pass
#                print("F", evid, "parent is reboot event", process_evid, binary, '....PID==4')
            else: # event belongs to PID 4
                pass
#                print("F", evid, "parent is reboot event", process_evid, binary, '....and PID<>4!  ', src_file )


        if parent_binary is not None:
            relation = (parent_binary, binary)

            item = self.pairs_same.get(relation)

            if not item:
                 item = self.pairs_var.get(relation)

            if not item:        # file event with no existing process pair
                item = self._create_process_container_on_the_fly(ev)


            if self.addfileop:
                t1_frags_without_file = ModelCmp4b._preprocess_file_for_special_dirs(item, src_file, ev[TYPE])
            else:
                t1_frags_without_file = ModelCmp4b._preprocess_file_for_special_dirs(item, src_file, None)

            self.add_prefix(item[MYDIR_PREFIX], t1_frags_without_file)

            if fileop == RENAME:
                dst_file = ev[DST_FILE_NAME]

                if self.addfileop:
                    t2_frags_without_file = ModelCmp4b._preprocess_file_for_special_dirs(item, dst_file, ev[TYPE])
                else:
                    t2_frags_without_file = ModelCmp4b._preprocess_file_for_special_dirs(item, dst_file, None)
                self.add_prefix(item[MYDIR_PREFIX], t2_frags_without_file)

#                 t2_frags_without_file = self._path_to_fragments_without_file(dst_file)
# #                t2 = tuple(map(len,t2_frags_without_file))
# #                print(dst_file, "", t2_frags_without_file, "", t2)
#
#                 l = len(item[BIN_TUPL_CUT])
#                 if t2_frags_without_file[:l] == item[BIN_FRAG_CUT]:   # if t2[:l]== binentry[BIN_TUPL_CUT]:
#                     t2_frags_without_file = ["EXEDIR"]+t2_frags_without_file[l:]
# #                    t2 = (-99,)+t2[l:]
#
#                 # access in root, so rise by one virtual ROOT directory
#                 if len(t2_frags_without_file)==0:
# #                    print("D", src_file, evid)
#                     filename = self._path_to_fragments_with_file(dst_file)[-1]
#                     t2_frags_without_file = ["ROOT"]
# #                    t2 = (-90,len(filename))
#
# #                print(dst_file, "", t2_frags_without_file, "", t2)
#
#                 self.add_prefix(item[MYDIR_PREFIX], t2_frags_without_file)



            item[LAST_EVENT]  = evid
            item[LAST_TIME]   = timestamp

#            self._add_one_to_key_(item[MYDIR_TUPL], t1)
#            if t2:
#                self._add_one_to_key_(item[MYDIR_TUPL], t2)


##############################################################################

    def consume_event(self, ev: dict):

        if not self.last_event_consumed:  # this is first event consumed
            if not self.fromreboot:    # and not from reboot
                self.set_reboot(ev)       # first event is reboot by force

        if ev[SEQUENCE_ID]==0 and ev[PARENT_ID]==None:
            self.set_reboot(ev)


        if self.rebootid:
            Filter.run_filters(ev)
            # pid         = ev[PID]            # ignore
            # parent_id   = ev[PARENT_ID]      # replaced by PARENT_PROCESS_NAME
            # sequence_id = ev[SEQUENCE_ID]    # ignore
            type_id   = ev[TYPE_ID]
            self.total_events +=1


            if type_id == PROCESS:
                self.total_events_process +=1
                self.consume_process(ev)

            elif type_id == FILE:
                self.total_events_file +=1
                self.consume_file(ev)

            elif ev[TYPE_ID] == NETWORK:
                self.total_events_network +=1
                if self.addnetwork:
                    self.consume_network(ev)


            elif ev[TYPE_ID] == REGISTRY:
                self.total_events_registry +=1
                reg_path = ev[PATH]
                reg_key = ev[KEY]

            elif ev[TYPE_ID] == THREAD:
                self.total_events_thread +=1

            else:
                print("bug! unknown event type!")
                exit(1)


#            if ev[TIME] > self.tick_start:
#                self.one_tick(ev)

            self.last_event_consumed = ev


    def one_tick(self, ev):
#        print(">>>TICK:", printNiceTimeDelta(ev[RELTIME]), ev[TIME])
        self.do_evaluation()

        self.tick_start = self.tick_end
        self.tick_end = self.tick_start + self.tick_delta

#        self.save_state(ev[RELTIME])
        self.save_state(ev[TIME])



    @staticmethod
    def is_exename_fuzzy_friend(localpair, testpair) -> bool:
        # # check for equal number of fragments
        # if len(localpair[BIN_FRAG]) == len(testpair[BIN_FRAG]) and \
        #    len(localpair[PAR_TUPL]) == len(testpair[PAR_TUPL]):
        #
        #     # total length max difference is <2
        #     if abs( sum(localpair[PAR_TUPL])-sum(testpair[PAR_TUPL]) )<2 and \
        #        abs( sum(localpair[BIN_TUPL])-sum(testpair[BIN_TUPL]) )<2:

        # check for identical fragments+size    (_CUT for ignore size of last fragment (exe))
        if  localpair[PAR_TUPL] == testpair[PAR_TUPL] and \
            localpair[BIN_TUPL] == testpair[BIN_TUPL]:

                # find number and location of differing frags
                index_different_par_frags=[]
                index_different_bin_frags=[]

                for index in range(len(localpair[PAR_TUPL])):
                    if localpair[PAR_FRAG][index]!=testpair[PAR_FRAG][index]:
                        index_different_par_frags.append(index)
#                        if abs( len(localpair[PAR_FRAG][index]) - len(testpair[PAR_FRAG][index]))<2:
#                            index_different_par_frags.append(index)
#                        else:
#                            return False   # one frag sizeably different

                for index in range(len(localpair[BIN_TUPL])):
                    if localpair[BIN_FRAG][index]!=testpair[BIN_FRAG][index]:
                        index_different_bin_frags.append(index)
#                        if abs( len(localpair[BIN_FRAG][index]) - len(testpair[BIN_FRAG][index]))<2:
#                            index_different_bin_frags.append(index)
#                        else:
#                            return False   # one frag sizeably different

                # max 2 different fragments allowed
                if len(index_different_par_frags)<3 and len(index_different_bin_frags)<3:
                    itsok = True

                    # a parent with only one frag is only sanely a REBOOT, SYSTEM or DUMMY,
                    # so this single frag must be identical
                    if len(localpair[PAR_TUPL])==1 and \
                                   localpair[PAR_TUPL][0] != testpair[PAR_TUPL][0]:
                        itsok = False

                    # last fragment (=exe name) must be one different fragment when two fragments differ
                    lastindexp = len(localpair[PAR_FRAG])-1
                    if len(index_different_par_frags)==2:
                        if index_different_par_frags[-1]==lastindexp:
                            pass
                        else:
                            itsok = False

                    lastindexb = len(localpair[BIN_FRAG])-1
                    if len(index_different_bin_frags)==2:
                        if index_different_bin_frags[-1]==lastindexb:
                            pass
                        else:
                            itsok = False

    #                print("1 :",localpair[PAIR], itsok, len(index_different_par_frags), index_different_par_frags)
    #                print(" 2:",testpair[PAIR], itsok, len(index_different_bin_frags), index_different_bin_frags)


                    if itsok is True:
#                        if len(index_different_bin_frags)>0:
#                         if len(index_different_bin_frags)==2 or len(index_different_par_frags)==2:
#                             print("sea:", localpair[PAIR][0], " ===> ", localpair[PAIR][1] )
#                             print("  ?:", testpair[PAIR][0], " ===> ", testpair[PAIR][1],
#                                   index_different_par_frags, lastindexp, "-",
#                                   index_different_bin_frags, lastindexb, )
                        return True
                    else:
                        return False
        return False



    def eval_same(self, force=False):
        for looppair in self.pairs_same:
            pair = self.pairs_same[looppair]
            friend = pair[FRIEND]

            if friend is None:
                print("bug! same has None friend!")
                print(pair[PAIR])
                exit(1)

            needs_reevaluation = force

            if pair[LAST_EVENT] != pair[EVAL_EVENT]:
                ModelCmp4b.calc_one_nilsimsa(pair[MYDIR_PREFIX], pair[MYDIR_PRENIL], pair[BIN_TUPL])
                needs_reevaluation = True

            if friend[LAST_EVENT] != friend[EVAL_EVENT]:
                ModelCmp4b.calc_one_nilsimsa(friend[MYDIR_PREFIX], friend[MYDIR_PRENIL], friend[BIN_TUPL])
                needs_reevaluation = True

            if needs_reevaluation:
                result = ModelCmp4b.eval_one_pair(pair, friend)
                pair[EVAL_STATE] = result

                if result[0] == 0:
                    if result[1]==0:
                        pair[EVAL_TYPE] = TSAME_IDENT
                    else:
                        pair[EVAL_TYPE] = TSAME_SYM
                else:
                    pair[EVAL_TYPE] = TSAME_ASYM
#
                pair[EVAL_EVENT] = pair[LAST_EVENT]
                 # don't update friend[EVAL_EVENT] here, this is done from the other side


    def eval_var(self):
        for looppair in self.pairs_var:
            pair = self.pairs_var[looppair]

            if pair[LAST_EVENT] != pair[EVAL_EVENT]:
                ModelCmp4b.calc_one_nilsimsa(pair[MYDIR_PREFIX], pair[MYDIR_PRENIL], pair[BIN_TUPL])
                pair[EVAL_EVENT] = pair[LAST_EVENT]

            result = None
            friend = None
            tyype  = None

            if self.other:
                for otherpair in self.other.pairs_var:
                    testfriend = self.other.pairs_var[otherpair]

                    if ModelCmp4b.is_exename_fuzzy_friend(pair, testfriend):
                        if testfriend[LAST_EVENT] != testfriend[EVAL_EVENT]:
                            ModelCmp4b.calc_one_nilsimsa(testfriend[MYDIR_PREFIX], testfriend[MYDIR_PRENIL], testfriend[BIN_TUPL])
                            testfriend[EVAL_EVENT] = testfriend[LAST_EVENT]

                        newresult = ModelCmp4b.eval_one_pair(pair, testfriend)
                        newfriend = testfriend

                        if newresult[0] == 0:
                            if newresult[1]==0:
                                newtyype = TFUZ_IDENT
                            else:
                                newtyype = TFUZ_SYM
                        else:
                            # no fuzzy match if mismatched prefixes == number of prefixes, that's a crap match
                            if newresult[0]==len(pair[MYDIR_PREFIX]):
                                continue
                            else:
                                newtyype = TFUZ_ASYM

                        if result:
                            if newresult[0]>result[0]:  # more prefixes wrong than best result
                                continue

                            if newresult[0]<result[0]:  # less, so surely better, take it
                                result = newresult
                                friend = newfriend
                                tyype = newtyype
                                continue

                            if newresult[1]<result[1]:  # same prefixes, but less hash distance
                                result = newresult
                                friend = newfriend
                                tyype = newtyype

                        else:   # first result ever -> take it
                            result = newresult
                            friend = newfriend
                            tyype = newtyype

            if result:  # one fuzzy friend was found
                pair[EVAL_STATE] = result
                pair[EVAL_TYPE] = tyype
                pair[FRIEND] = friend
            else:       # we are alone :-(
                pair[EVAL_STATE] = None
                pair[EVAL_TYPE] = TUNIQUE
                pair[FRIEND] = None



    @staticmethod
    def common_tuple_prefix_with1random(a,b):
        i=0
        while i<len(a) and i<len(b) and a[i]==b[i]:
            i+=1
        if i<len(a) and i<len(b):
            if len(a[i])==len(b[i]):    # one random element of same length allowed
                wascutoff = i
                i+=1
                while i<len(a) and i<len(b) and a[i]==b[i]:  # try others
                    i+=1
                return a[:i],b[:i]
    #            if i>wascutoff+1:  # alternatively: only accept longer if one same beyond random element
    #                return a[:i],b[:i]
    #            else:
    #                return a[:wascutoff],b[:wascutoff]
            else:
                return a[:i],b[:i]
        else:
            return a[:i],b[:i]



    @staticmethod
    def eval_prefixes(inpair, infriend):
        mypre = sorted(inpair[MYDIR_PREFIX])
        frpre = sorted(infriend[MYDIR_PREFIX])

        missing_prefixes = 0   # number of
        total_dist = 0         # sum of all hash distances
        result = {}

        while len(mypre)>0 or len(frpre)>0:
            val = None

            if len(mypre)==0:
                if len(frpre)>0:
                    val = frpre.pop(0)
#                    print("LONELY2", val)
                    continue
                else: # both empty
                    break
            else:
                if len(frpre)==0:
                    val = mypre.pop(0)
#                    print("LONELY1", val)
                    missing_prefixes += 1
                    continue
                else:
                    if mypre[0]<frpre[0]:
                        if mypre[0][0] != frpre[0][0]:
                            val = mypre.pop(0)
#                            print("LONELY1", val)
                            missing_prefixes += 1
                            continue
                    else:
                        if mypre[0][0] != frpre[0][0]:
                            val = frpre.pop(0)
#                            print("LONELY2", val)
                            continue


            myprefix  = mypre.pop(0)
            friprefix = frpre.pop(0)
            distpre = ModelCmp4b._nilsimsa_distance_( inpair[MYDIR_PRENIL][myprefix],
                                                    infriend[MYDIR_PRENIL][friprefix] )

            if myprefix == friprefix:   # identical prefix, that's easy
                result[myprefix] = (myprefix, myprefix, distpre, None, None, distpre)
                total_dist += distpre

            else:   # find common prefix first
#                print("C1  ", myprefix)
#                print("C2  ", friprefix)
                common1, common2 = ModelCmp4b.common_tuple_prefix_with1random(myprefix, friprefix)
#                print("--->", common1, "", common2)

                if len(common1)<len(myprefix):
#                    print(" MINE   ")

                    locstore = {}
                    locstore[myprefix] = deepcopy(inpair[MYDIR_PREFIX][myprefix])
                    ModelCmp4b.add_prefix(locstore, common1)
                    ModelCmp4b.decrease_prefix(locstore, common1)
                    newmyprefix = common1
                    newmynil = ModelCmp4b.calc_one_nilsimsa_for_one_prefix(common1, locstore[common1], inpair[BIN_TUPL])
                else:
                    newmyprefix = myprefix
                    newmynil = inpair[MYDIR_PRENIL][myprefix]


                if len(common2)<len(friprefix):
#                    print("  FRIEND")

                    locstore = {}
                    locstore[friprefix] = deepcopy(infriend[MYDIR_PREFIX][friprefix])
                    ModelCmp4b.add_prefix(locstore, common2)
                    ModelCmp4b.decrease_prefix(locstore, common2)
                    newfriprefix = common2
                    newfrinil = ModelCmp4b.calc_one_nilsimsa_for_one_prefix(common2, locstore[common2], infriend[BIN_TUPL])

                else:
                    newfriprefix = friprefix
                    newfrinil = infriend[MYDIR_PRENIL][friprefix]

                distpost = ModelCmp4b._nilsimsa_distance_( newmynil, newfrinil)
                total_dist += distpost

                result[myprefix] = (myprefix, friprefix,     distpre,
                                 newmyprefix, newfriprefix,  distpost)
#                print("##", distpre, "-->", distpost)
#                print("")

#            result[myprefix] = (myprefix, myprefix, 99)


        return (missing_prefixes, total_dist, result)



    @staticmethod
    def eval_one_pair(inpair, infriend):

        # same number of prefixes
        if len(inpair[MYDIR_PREFIX]) == len(infriend[MYDIR_PREFIX]):
            myhashes    = set(inpair[MYDIR_PRENIL].values())
            otherhashes = set(infriend[MYDIR_PRENIL].values())
            # and hashes identical
            if myhashes == otherhashes:
                return (0,0, None)      # we are IDENT

        result = ModelCmp4b.eval_prefixes(inpair, infriend)
        return result


##############################################################################



    def print_result(self, result=None):
        if not result:
            return

        result = int(result)

        if result == 0:
            print("supported results:")
            print("21 - unique prefix dirs per host")
#            print("30 - raw dump of all prefixes and hashes")
#            print("40 - r4 matcher by end of run evaluation")
            print("50 - r4 matcher by periodic tick evaluation")
            print("60 - suspicious pairs summary - summary")
            print("61 - suspicious pairs summary - with file access details")
            print("69 - suspicious pairs summary - you know want you want")
            print("70 - suspicious pairs summary - overview event ordered")
            print("71 - suspicious pairs summary - overview + event details")
            print("72 - suspicious pairs summary - only detailed list of events")
            pass


        if result == 1:
            print("hello world!")
            pass


        elif result == 21:
            alldirs = {}
            max1 = ModelCmp4b.addup_root_dirs(alldirs, self.pairs_same)
            max2 = ModelCmp4b.addup_root_dirs(alldirs, self.pairs_var)

            otherdirs = {}
            max3 = ModelCmp4b.addup_root_dirs(otherdirs, self.other.pairs_same)
            max4 = ModelCmp4b.addup_root_dirs(otherdirs, self.other.pairs_var)


            for prefixkey in sorted(alldirs):
                if prefixkey in otherdirs:
                    col = rt.setfg(CLIGHTGREEN)
                else:
                    col = rt.setfg(CLIGHTRED)
                print(col, str(alldirs[prefixkey]).rjust(4)+"x", "\\"+("\\".join(prefixkey)), rt.resetfg() )

            print("")
            print("same pairs", len(self.pairs_same))
            print(" var pairs", len(self.pairs_var))
            print("   -->", len(alldirs), "prefixes in total  ","max per pair: "+str(max(max1,max2,max3,max4)))


        elif result == 30:
            alldirs = {}
            max1 = ModelCmp4b.addup_root_dirs(alldirs, self.pairs_same)
            max2 = ModelCmp4b.addup_root_dirs(alldirs, self.pairs_var)

            otherdirs = {}
            max3 = ModelCmp4b.addup_root_dirs(otherdirs, self.other.pairs_same)
            max4 = ModelCmp4b.addup_root_dirs(otherdirs, self.other.pairs_var)

            print("   ||| SAME |||")
            ModelCmp4b.dump_prefix_and_nil(self.pairs_same)
            print("   ||| VAR |||")
            ModelCmp4b.dump_prefix_and_nil(self.pairs_var)


        elif result == 40:
            ModelCmp4b.dump_current_matching_old(self.pairs_same, self.pairs_var)


        elif result >=50 and result <=59:
            self.do_evaluation(force=True)

            ModelCmp4b.dump_current_states(self.pairs_same, self.pairs_var, self.reboots)
            print("")

        elif result >=60 and result <=79:
            self.do_evaluation(force=True)

            self.pretty_print_for_humans(result)
            print(rt.resetfg())



    def do_evaluation(self,force=False):
        self.eval_same(force)
        self.eval_var()
        if self.other:
            self.other.eval_same(force)
            self.other.eval_var()


##############################################################################


    @staticmethod
    def addup_root_dirs(allprefix, inpairs):
        max_prefixes = 0
        for pair in inpairs:
            p = inpairs[pair]
            if len(p[MYDIR_PREFIX]) > max_prefixes:
                max_prefixes = len(p[MYDIR_PREFIX])
            for prefixkey in p[MYDIR_PREFIX]:
                ModelCmp4b._add_one_to_key_(allprefix, prefixkey)
        return max_prefixes


    @staticmethod
    def calc_one_nilsimsa_for_one_prefix(prefix: tuple, prefixdata:dict, bintupl:dict) -> Nilsimsa:
        n = Nilsimsa()

        n.process("\\"+"\\".join(prefix) )             # prefix in text
#                print("nnn: \\"+"\\".join(prefix) )
#                print(prefix)
        if prefix==("EXEDIR",):                           # if EXEDIR additionally numbers tupl of binary
            for index, item in enumerate(bintupl):             # binary
                n.process("\\"+str(item) )    # +chr(97+index)
#                        print("nne \\"+str(item) )

        for thistuple in sorted(prefixdata):   # detail number tupls
            for index, item in enumerate(thistuple):
                n.process("\\"+str(item)+chr(97+index) )
#                        print("nn+ \\"+str(item)+chr(97+index) )

        return n


    @staticmethod
    def calc_one_nilsimsa(inprefixes:dict, nilstore:dict, bintupl:dict):
            nilstore.clear()
            for prefix in inprefixes:
                n = ModelCmp4b.calc_one_nilsimsa_for_one_prefix(prefix, inprefixes[prefix], bintupl)
                nilstore[prefix] = n


    @staticmethod
    def dump_prefix_and_nil(inpairs):
        for looppair in sorted(inpairs):
            pair = inpairs[looppair]

            print(rt.setfg(CVIO3), pair[PAIR][0], rt.setfg(CNORM), "===>",
                  rt.setfg(CVIO3), pair[PAIR][1], rt.resetfg())

            ModelCmp4b.calc_one_nilsimsa(pair[MYDIR_PREFIX], pair[MYDIR_PRENIL], pair[BIN_TUPL])
            myprefixes = sorted(pair[MYDIR_PREFIX])
            friend = pair[FRIEND]

            otherprefixes = []
            sharedprefixes = {}
            uniqueprefixes = {}

            if friend:
                ModelCmp4b.calc_one_nilsimsa(friend[MYDIR_PREFIX], friend[MYDIR_PRENIL], friend[BIN_TUPL])
                otherprefixes = sorted(friend[MYDIR_PREFIX])
                sharedprefixes = set(myprefixes) & set(otherprefixes)
                uniqueprefixes = set(myprefixes) ^ set(otherprefixes)

            for prefixkey in myprefixes:
                # if prefixkey in sharedprefixes:
                #     col = CLIGHTGREEN
                #     dist = str( 128-compare_digests(pair[MYDIR_PRENIL][prefixkey].hexdigest(),
                #                                   friend[MYDIR_PRENIL][prefixkey].hexdigest()) ).rjust(3)
                # else:
                #     if friend:
                #         match = ModelCmp4b.find_me_a_nil_friend(pair[MYDIR_PREFIX], friend[MYDIR_PREFIX],
                #                                                  prefixkey,
                #                                                 pair[MYDIR_PRENIL], friend[MYDIR_PRENIL],
                #                                                 pair[BIN_TUPL], friend[BIN_TUPL])
                #     col = CDARKRED
                #     dist = " ? "

                print("    ",
                      rt.setfg(CDARK), pair[MYDIR_PRENIL][prefixkey],
                      rt.setfg(CNORM), "  \\"+"\\".join(prefixkey), rt.resetfg() )


            # if friend:
            #     for prefixkey in sorted(otherprefixes):
            #         if prefixkey not in sharedprefixes:   # not seen before
            #             print("      ",
            #                   rt.setfg(CDARK), friend[MYDIR_PRENIL][prefixkey],
            #                   rt.setfg(CDARKRED) , " ?  \\"+"\\".join(prefixkey), rt.resetfg() )


    @staticmethod
    def dump_current_matching_old(inpairs_same, inpairs_var):
        print("   <<< SAME >>>")

        same_ident = []
        same_sym  = []
        same_asym = []

        for looppair in sorted(inpairs_same):
            pair = inpairs_same[looppair]
            friend = pair[FRIEND]

            ModelCmp4b.calc_one_nilsimsa(pair[MYDIR_PREFIX], pair[MYDIR_PRENIL], pair[BIN_TUPL])
            myprefixes = set(sorted(pair[MYDIR_PREFIX]))

#            if friend:  # here always true for same
            ModelCmp4b.calc_one_nilsimsa(friend[MYDIR_PREFIX], friend[MYDIR_PRENIL], friend[BIN_TUPL])
            otherprefixes = set(sorted(friend[MYDIR_PREFIX]))
            sharedprefixes = set(myprefixes) & set(otherprefixes)
            uniqueprefixes = set(myprefixes) ^ set(otherprefixes)

            if len(uniqueprefixes)==0:  # same prefixes
                myhashes    = set(pair[MYDIR_PRENIL].values())
                otherhashes = set(friend[MYDIR_PRENIL].values())
                if myhashes == otherhashes:           # hashes identical
                    same_ident.append(looppair)
                else:
                    same_sym.append(looppair)
            else:
                same_asym.append(looppair)


        if len(same_ident)>0:   # same prefixes AND hashes
            for looppair in same_ident:
                pair = inpairs_same[looppair]
                print(rt.setfg(CNORM)+"SAME_IDENT",
                      rt.setfg(CLIGHTGREEN),str(len(pair[MYDIR_PREFIX])), " ",
                      rt.setfg(CVIO3), pair[PAIR][0], rt.setfg(CNORM), "===>",
                      rt.setfg(CVIO3), pair[PAIR][1], rt.resetfg())

        if len(same_sym)>0:     # same prefixes, different hashes
            for looppair in same_sym:
                pair = inpairs_same[looppair]
                friend = pair[FRIEND]

                myhashes    = set(pair[MYDIR_PRENIL].values())
                otherhashes = set(friend[MYDIR_PRENIL].values())

                myprefixes = set(sorted(pair[MYDIR_PREFIX]))


                if myhashes == otherhashes:           # hashes identical
                    print(rt.setfg(CNORM)+"SAME_IDENT",
                          rt.setfg(CLIGHTGREEN),str(len(myprefixes)), " ",
                          rt.setfg(CVIO3), pair[PAIR][0], rt.setfg(CNORM), "===>",
                          rt.setfg(CVIO3), pair[PAIR][1], rt.resetfg())
                else:    # hashes different
                    print(rt.setfg(CNORM)+"SAME_SYM  ",
                          rt.setfg(CLIGHTGREEN),str(len(myprefixes)), " ",
                          rt.setfg(CVIO2), pair[PAIR][0], rt.setfg(CNORM), "===>",
                          rt.setfg(CVIO2), pair[PAIR][1], rt.resetfg())

                    for prefixkey in myprefixes:
                        valueme    = pair[MYDIR_PRENIL][prefixkey].hexdigest()
                        valueother = friend[MYDIR_PRENIL][prefixkey].hexdigest()
                        if valueme == valueother:
                            col = CLIGHTGREEN   # this prefix hash same
                            dist = "== "
                        else:
                            col = CDARKGREEN    # this prefix hash different
                            dist = str( 128-compare_digests(valueme,valueother) ).rjust(3)

                        print("     ",
                              rt.setfg(CDARK), pair[MYDIR_PRENIL][prefixkey],
                              rt.setfg(col), dist,
                              "  \\"+"\\".join(prefixkey), rt.resetfg() )


        if len(same_asym)>0:    # not same prefixes
            for looppair in same_asym:
                pair = inpairs_same[looppair]
                friend = pair[FRIEND]

                myprefixes = set(pair[MYDIR_PREFIX])

                print(rt.setfg(CNORM)+"SAME_ASYM ",
                      rt.setfg(CLIGHTGREEN),str(len(myprefixes)), " ",
                      rt.setfg(CVIO1), pair[PAIR][0], rt.setfg(CNORM), "===>",
                      rt.setfg(CVIO1), pair[PAIR][1], rt.resetfg())
#                print(myprefixes)
#                print(otherprefixes)

                for prefixkey in myprefixes:
#                    print(prefixkey)
#                    print(pair[MYDIR_PRENIL][prefixkey])
#                    print(friend[MYDIR_PRENIL][prefixkey])
                    match = None

                    if prefixkey in friend[MYDIR_PRENIL] and pair[MYDIR_PRENIL][prefixkey] == friend[MYDIR_PRENIL][prefixkey]:
                        col = CLIGHTGREEN  # for this prefix hash same
                        dist = "000"
                    else:
                        if prefixkey in friend[MYDIR_PRENIL]:
                            col = CDARKGREEN   # same prefix
                            dist = str( 128-compare_digests(pair[MYDIR_PRENIL][prefixkey].hexdigest(),
                                                          friend[MYDIR_PRENIL][prefixkey].hexdigest()) ).rjust(3)
                        else:
                            col = CLIGHTRED    # unknown prefix, needs further comparison
                            dist = '???'

                            # [wasprefix, isprefix, newdist]
                            match = ModelCmp4b.find_me_a_nil_friend(pair[MYDIR_PREFIX], friend[MYDIR_PREFIX],
                                                                       prefixkey,
                                                                       pair[MYDIR_PRENIL], friend[MYDIR_PRENIL],
                                                                       pair[BIN_TUPL], friend[BIN_TUPL])
                            if match:
                                col = CDARKRED

                    print("     ",
                          rt.setfg(CDARK), pair[MYDIR_PRENIL][prefixkey],
                          rt.setfg(col), dist, "  \\"+"\\".join(prefixkey), rt.resetfg() )

                    for tupl in sorted(pair[MYDIR_PREFIX][prefixkey]):
                        print(rt.setfg(CVIO1),"                                                                                " + \
                              str(tupl)+"  x"+str(pair[MYDIR_PREFIX][prefixkey][tupl]) )

                    if match:
                        print("     ",
                              rt.setfg(CDARK), "                                                                ",
                              rt.setfg(CLIGHTGREEN), str(match[2]).rjust(3), " "+match[0], rt.resetfg() )

        print(rt.resetfg())
        print("   <<< VAR >>>")
        for looppair in sorted(inpairs_var):
            pair = inpairs_var[looppair]
            friend = pair[FRIEND]

            print(rt.setfg(CNORM)+"          ",
                  rt.setfg(CLIGHTGREEN),str(len(pair[MYDIR_PREFIX])), " ",
                  rt.setfg(CDARKRED),  pair[PAIR][0], rt.setfg(CNORM), "===>",
                  rt.setfg(CLIGHTRED), pair[PAIR][1], rt.resetfg())

###############################################################################
    @staticmethod
    def print_prefixes(inpair):
        pair = inpair

        if pair[EVAL_STATE]:
            estate = pair[EVAL_STATE][2]
        else:
            estate = None

        for prefixkey in sorted(pair[MYDIR_PREFIX]):
            uplift = " "
            path = "\\".join(prefixkey)
            pathuplift =""
            if estate and prefixkey in estate:
                col = CLIGHTGREEN

                dist = estate[prefixkey][2+3]    # dist calculated
                if estate[prefixkey][2]-estate[prefixkey][2+3]>0:  # uplift check
                    uplift = "^"
                    temppath=path
                    path = "\\".join(estate[prefixkey][3])
                    pathuplift = rt.setfg(CDARK)+temppath[len(path):]
                if dist==0:
                    distcol=CLIGHTGREEN
                else:
                    distcol=CDARKGREEN
                dist = str(dist).rjust(3)

            else:
                col = CLIGHTRED
                dist = "---"
                distcol = CLIGHTRED

            nils = pair[MYDIR_PRENIL][prefixkey]

            tupl_count = 0
            for tupl in pair[MYDIR_PREFIX][prefixkey]:
                tupl_count += pair[MYDIR_PREFIX][prefixkey][tupl]

            print("     ",
                  rt.setfg(CDARK), nils,
                  rt.setfg(distcol), dist+uplift,
                  rt.setfg(col), " \\"+path+pathuplift,
                  rt.setfg(CDARK), " x"+str(tupl_count), rt.resetfg() )


        #         #for tupl in sorted(pair[MYDIR_PREFIX][prefixkey]):
        #         #    print(rt.setfg(CVIO1),"                                                                                " + \
        #         #         str(tupl)+"  x"+str(pair[MYDIR_PREFIX][prefixkey][tupl]) )


    @staticmethod
    def evaltype2str(ty):
        if ty==TSAME_IDENT:
            return "SAME_IDENT"
        elif ty==TSAME_SYM:
            return "SAME_SYM  "
        elif ty==TSAME_ASYM:
            return "SAME_ASY  "

        elif ty==TFUZ_IDENT:
            return "FUZ_IDENT "
        elif ty==TFUZ_SYM:
            return "FUZ_SAME  "
        elif ty==TFUZ_ASYM:
            return "FUZ_ASYM  "

        elif ty==TUNIQUE:
            return "! UNIQ !  "
        else:
            print("help! unknown type of pair?", ty)
            ty[3] = 1
            exit(1)


    @staticmethod
    def print_one_pair(inpair):
            pair = inpair
            s = pair[EVAL_STATE]
            if s:
                if s[0]>0:
                    colprefixes = CLIGHTRED
                else:
                    colprefixes = CLIGHTGREEN
                prefixcount = str(s[0])
            else:
                colprefixes = CVIO2
                prefixcount = "?"

            if s:
                if s[1]>0:
                    coldist = CLIGHTRED
                else:
                    coldist = CLIGHTGREEN
                hashcount = str(s[1])
            else:
                coldist = CVIO2
                hashcount = "?"

            if (pair[EVAL_TYPE] == TSAME_IDENT) or \
               (pair[EVAL_TYPE] == TSAME_SYM):
                paircol = CLIGHTGREEN
            elif pair[EVAL_TYPE] == TSAME_ASYM:
                paircol = CLIGHTRED
            else:
                paircol = CVIO3

            if pair[EVAL_TYPE] == TSAME_ASYM:
                typecol = rt.setfg(CLIGHTRED)
            elif pair[EVAL_TYPE] == TFUZ_IDENT:
                typecol = rt.setfg(CLIGHTGREEN)
            elif pair[EVAL_TYPE] == TFUZ_SYM:
                typecol = rt.setfg(CDARKGREEN)
            elif (pair[EVAL_TYPE] == TFUZ_ASYM) or \
               (pair[EVAL_TYPE] == TUNIQUE):
                typecol = rt.setfg(CLIGHTRED)
            else:
                typecol = ""

            grandparent = ""
            colgrand = CDARKBLUE
            if len(pair[PARENT_PAIR])==1:
                gptupl = list(pair[PARENT_PAIR].keys()) [0]  # get only tuple key of dict
                gpentry = pair[PARENT_PAIR][gptupl][0]          # get data tuple
                grandparent = gpentry[0] [PAIR][0]
                gptype      = gpentry[0] [EVAL_TYPE]

#                grandparent = pair[PARENT_PAIR][PAIR][0]+'('+str(pair[PARENT_PAIR][PARENT_ID])+')'
                if gptype == TSAME_IDENT or gptype == TSAME_SYM:
                    colgrand = CLIGHTGREEN
                elif gptype == TSAME_ASYM:
                    colgrand = CLIGHTRED
                else:  # bug
                    colgrand = CVIO2

            gpexe, pexe, myexe = ModelCmp4b.find_executions_for_print(pair)

            # FIXME
            # We cannot go back to the db because we are a staticmethod :-(
            # if grandparent=="" and len(pair[EXECS])==1:
            #     procevent = self._get_process_from_database_(str(pair[EXECS][0][0]))
            #     grandparent = procevent[GRANDPARENT_PROCESS_NAME]

            print(str(pair[FIRST_EVENT]).rjust(8),
                  rt.setfg(CNORM)+typecol+ModelCmp4b.evaltype2str(pair[EVAL_TYPE]),
                  rt.setfg(CVIO1),str(len(pair[MYDIR_PREFIX])), " ",
                  rt.setfg(colprefixes),prefixcount+"|"+
                  rt.setfg(coldist),    hashcount.rjust(2), " ",

                  rt.setfg(colgrand), grandparent+gpexe, rt.setfg(CNORM), "===>",
                  rt.setfg(colgrand), pair[PAIR][0]+pexe, rt.setfg(CNORM), "===>",
                  rt.setfg(paircol), pair[PAIR][1]+myexe,
                  rt.setfg(CDARK), "x"+str(len(pair[EXECS])), rt.resetfg()) #, pair[LAST_EVENT], pair[EVAL_EVENT] )
            if pair[EVAL_TYPE] == TFUZ_IDENT or \
               pair[EVAL_TYPE] == TFUZ_SYM or \
               pair[EVAL_TYPE] == TFUZ_ASYM:
                print(rt.setfg(CDARK),
                      " "*(len(grandparent+gpexe)+41), pair[FRIEND][PAIR][0],
                      " "*(len(pexe)+6),               pair[FRIEND][PAIR][1] )

            ModelCmp4b.print_prefixes(pair)

    @staticmethod
    def sort_and_print_pairs_by_state(intuples, inpairs):
        temp = sorted(intuples, key= lambda bla: inpairs[bla][EVAL_STATE][0:2] )
        for looppair in temp:
            pair = inpairs[looppair]
            ModelCmp4b.print_one_pair(pair)


    @staticmethod
    def sort_and_print_pairs_by_time(intuples, inpairs, inreboots):
        temp = sorted(intuples, key= lambda bla: int(inpairs[bla][FIRST_EVENT]) )
        reboots = deepcopy(inreboots)

        for looppair in temp:
            pair = inpairs[looppair]

            while reboots and reboots[0]<int(pair[FIRST_EVENT]):
                print(rt.setfg(CTURQ)+str(reboots.pop(0)).rjust(8), "REBOOT", rt.resetfg())

            ModelCmp4b.print_one_pair(pair)

        while reboots:
            print(rt.setfg(CTURQ)+str(reboots.pop(0)).rjust(8), "REBOOT", rt.resetfg())


    @staticmethod
    def find_executions_for_print(inpair:dict) -> tuple:
        if len(inpair[EXECS])==1:
            myexe     = '('+str(inpair[EXECS][0][2])+")"
            parentexe = '('+str(inpair[EXECS][0][1])+')'
            gpexe     = '('+str(inpair[EXECS][0][0])+')'
        else:
            myexe = "(?x"+str(len(inpair[EXECS]))+")"
            s = set()
            for entry in inpair[EXECS]:
                s.add(entry[1])

            if len(s)==1:
                parentid = s.pop()
                parentexe = "("+str(parentid)+")"

                s = set()
                for entry in inpair[EXECS]:
                    if entry[1]==parentid:
                        s.add(entry[0])
            else:
                parentid = None
                parentexe = "(?x"+str(len(s))+")"

                s = set()
                for entry in inpair[EXECS]:
                    s.add(entry[0])

            if len(s)==1:
                parentid = s.pop()
                gpexe = "("+str(parentid)+")"
            else:
                gpexe = "(?x"+str(len(s))+")"

        return (gpexe, parentexe, myexe)



    def find_asym_prefixes(self, inpair) -> list:
        result = []

        pair = inpair

        if pair[EVAL_STATE]:
            estate = pair[EVAL_STATE][2]
        else:
            estate = None

        for prefixkey in sorted(pair[MYDIR_PREFIX]):

            if estate and prefixkey in estate:
                continue
            else:
                col = CVIO3

            tupl_count = 0
            for tupl in pair[MYDIR_PREFIX][prefixkey]:
                tupl_count += pair[MYDIR_PREFIX][prefixkey][tupl]

            result.append( (prefixkey, tupl_count, "\\"+"\\".join(prefixkey)) )
#            print(" "*(50+len(pair[PAIR][0])),
#                  rt.setfg(col), " \\"+path,
#                  rt.setfg(CDARK), " x"+str(tupl_count), rt.resetfg() )
        return result



    def _find_files_for_file_(self, src_file, prefixtext, prefixkey, ev, pair, knownfiles, allprocessids, resultverbosity):
                    if self.addfileop:
                        frags_without_filei = ModelCmp4b._preprocess_file_for_special_dirs(pair, src_file, ev[TYPE])
                    else:
                        frags_without_filei = ModelCmp4b._preprocess_file_for_special_dirs(pair, src_file, None)
                    frags_without_file = tuple(frags_without_filei)

    #                print(prefixkey, "   ", frags_without_file)

                    if len(prefixkey)<=len(frags_without_file):
                        if frags_without_file[0:len(prefixkey)] == prefixkey:

#                            print( ev[GRANDPARENT_PROCESS_NAME], ev[PARENT_PROCESS_NAME], ev[PROCESS_NAME],
#                                   "*", pair[PAIR][0], pair[PAIR][1] )

                            process_evid = int(ev[PARENT_ID])   # parent of file event is the process event == the process
                            allprocessids.add(process_evid)

                            if src_file in knownfiles:  # already seen once, no need to print again?
                                if resultverbosity < 69:
                                    return

                            ModelCmp4b._add_one_to_key_(knownfiles, src_file)

                            filenamefrag = ModelCmp4b._path_to_fragments_with_file(src_file)[-1]

                            middlepart = frags_without_file[len(prefixkey):]
                            if len(middlepart)==0:
                                pathsep = ""
                            else:
                                pathsep = "\\"

                            # (44+len(pair[PAIR][0])),
                            print(" " * 3,
                                  rt.setfg(CLIGHTGREEN) + FILEOP2STR[ev[TYPE]],
                                  rt.setfg(CNORM), ev[ID],
                                  rt.setfg(CDARK) + prefixtext +
                                  rt.setfg(CVIO2) + pathsep +"\\".join(middlepart) +
                                  rt.setfg(CNORM) +"\\" + filenamefrag,
                                  rt.resetfg())


    def _match_file_to_section_(self, src_file, prefixtext, prefixkey, ev, pair, knownfiles, exeids, uniquefiles):

                    if self.addfileop:
                        frags_without_filei = ModelCmp4b._preprocess_file_for_special_dirs(pair, src_file, ev[TYPE])
                    else:
                        frags_without_filei = ModelCmp4b._preprocess_file_for_special_dirs(pair, src_file, None)
                    frags_without_file = tuple(frags_without_filei)

                    if len(prefixkey)<=len(frags_without_file):                # prefix shorter than file
                        if frags_without_file[0:len(prefixkey)] == prefixkey:  # prefix matches

                            # if src_file in knownfiles:  # already seen once, no need to print again?
                            #     return
                            # ModelCmp4b._add_one_to_key_(knownfiles, src_file)
                            #
                            filenamefrag = ModelCmp4b._path_to_fragments_with_file(src_file)

                            uniquefiles.add(src_file)

                            if len(filenamefrag)>0:
                                filenamefrag = filenamefrag[-1]
                                middlepart = frags_without_file[len(prefixkey):]
                                if len(middlepart)==0:
                                    pathsep = ""
                                else:
                                    pathsep = "\\"

                                knownfiles.append( [int(ev[ID]), ev, (prefixtext, pathsep +"\\".join(middlepart), "\\" + filenamefrag) ] )
                            else:
                                knownfiles.append( [int(ev[ID]), ev, ("",         ""                            , "\\" + src_file) ] )

                            exeids.add(int(ev[PARENT_ID]))  # and remember our parent


    def _print_wiped_(self, pair, hasprefixes):
            typecol = self._suspicioustype_to_col(pair)

#                          rt.setfg(CNORM), str(item[0])+" ",
#                          rt.setfg(CNORM), str(item[1])+" ",
            if hasprefixes==None:
                finish = "process probably executed about here (with no file accesses)"
            else:
                finish = "process finished about here"
            print("    ",
                  rt.setfg(CDARK), pair[PAIR][0],
                  rt.setfg(CNORM), "===>", typecol, pair[PAIR][1],
                  rt.setfg(CDARK), finish, rt.resetfg() )
#                          rt.setfg(CDARK), "x"+str(len(pair[EXECS])), rt.resetfg() )


    def find_files_for_all_sections(self, first_event, last_event, allsections):
        #          0                 1            2   3minexeid   4    5files         6            7
        # (pair[FIRST_EVENT], pair[LAST_EVENT], pair, None, pretupl,  [accesses], set(parentids), set(uniqfiles) )
                                                     #   (prefixkeytupl, count, prefixintext)
        localranges = deepcopy(self.ranges_consumed)
#        pprint(localranges)

        while True:  # optimize ranges to re-run
            if len(localranges)==0:
                break

            if localranges[0][1]<first_event:
                r = localranges.pop(0)
#                print("removed front range:", r)
                continue    # try again, there may be more than one

            if localranges[0][0]<first_event:
#                print("adjusted start from:", localranges[0][0], "to", first_event)
                localranges[0][0] = first_event

            if localranges[-1][0]>last_event:
                r = localranges.pop(len(localranges)-1)
#                print("removed end range:", r)
                continue    # try again, there may be more than one

            if last_event<localranges[-1][1]:
#                print("adjusted end from:", localranges[0][1], "to", last_event)
                localranges[-1][1]=last_event

            break   # if we got here, all ranges should be fixed, so exit

#        pprint(localranges)

        while len(localranges)>0:
            first_event, last_event = localranges.pop(0)
#            print("querying db for details in", first_event, "--", last_event)

            resprox = self.dr.read_sql_file(first_event, last_event)
            if int(resprox.rowcount)==0:
                print(rt.resetfg(),"WARNING! queried for events in", str(first_event), "to", str(last_event), "but got 0 file events?")
                continue

            events_toread = int(resprox.rowcount)

            sections_done = []

            while events_toread>0:
                ev = row2dict(resprox.fetchone())
                evid = int(ev[ID])
                toremove = []

                i = 0
                for index, item in enumerate(allsections):  # look for event in all sections
                    item = allsections[index]

                    if item[1]<evid:           # this section is done, remove it
                        toremove.append(index)
                        continue

                    if evid>=item[0]:   # may be in this section

    #                    if item[4] is None:     # no file accesses -> immediately done
    #                        toremove.append(index)
    #                        continue

                        Filter.run_filters(ev)
                        pair = item[2]

                        # is this section the correct pair?
                        if ev[GRANDPARENT_PROCESS_NAME] == pair[PAIR][0] and \
                                ev[PARENT_PROCESS_NAME] == pair[PAIR][1]:

                                knownfiles  = item[5]
                                exeids      = item[6]
                                uniquefiles = item[7]

                                fileop   = ev[TYPE]
                                src_file = ev[SRC_FILE_NAME]

                                if fileop == RENAME:
                                    ev[TYPE] = RENAME_SRC

                                for prefix in item[4]:
                                    prefixkey  = prefix[0]
                                    prefixtext = prefix[2]
                                    self._match_file_to_section_(src_file, prefixtext, prefixkey, ev, pair, knownfiles, exeids, uniquefiles)

                                if fileop == RENAME:
                                    dst_file = ev[DST_FILE_NAME]
                                    ev[TYPE] = RENAME_DST

                                    for prefix in item[4]:
                                        prefixkey  = prefix[0]
                                        prefixtext = prefix[2]
                                        self._match_file_to_section_(dst_file, prefixtext, prefixkey, ev, pair, knownfiles, exeids, uniquefiles)


                if len(toremove)>0:
                    for index in reversed(toremove):
                        sections_done.append( allsections.pop(index) )

                events_toread -=1


        while len(allsections)>0:
            sections_done.append( allsections.pop(0) )

        return sections_done


    def find_files_for_prefix(self, pair, intupl, resultverbosity):
        prefixkey = intupl[0]
        count = intupl[1]

        prefixtext = "\\"+"\\".join(prefixkey)

        if count==0:
            print("BUG! searching for prefix", prefixtext,"but expecting 0 files?")
            exit(1)

        if resultverbosity!= 61:
            print(" "*(18),  #+len(pair[PAIR][0])),      # 53
                  rt.setfg(CTURQ), prefixtext,
                  rt.setfg(CDARK), " x"+str(count),
                  rt.resetfg() )

        if resultverbosity==60:
            return

        if resultverbosity==69:
            for tupl in sorted(pair[MYDIR_PREFIX][prefixkey]):
                print(rt.setfg(CVIO1)," "*20 + \
                      str(tupl)+"  x"+str(pair[MYDIR_PREFIX][prefixkey][tupl]) )



        resprox = self.dr.read_sql_file(pair[FIRST_EVENT], pair[LAST_EVENT])
#                                        pair[PAIR][0],pair[PAIR][1])
        if int(resprox.rowcount)==0:
            print(rt.resetfg(),"BUG! queried for events in", pair[FIRST_EVENT], "to", pair[LAST_EVENT], "but got 0 events?")
            exit(1)

        events_toread = int(resprox.rowcount)

        knownfiles = {}
        allprocessids = set()

        while events_toread>0:
            ev = row2dict(resprox.fetchone())
            if ev[TYPE_ID] == FILE:
                Filter.run_filters(ev)

                if ev[GRANDPARENT_PROCESS_NAME] == pair[PAIR][0] and \
                        ev[PARENT_PROCESS_NAME] == pair[PAIR][1]:

                    fileop   = ev[TYPE]

                    src_file = ev[SRC_FILE_NAME]
                    self._find_files_for_file_(src_file, prefixtext, prefixkey, ev, pair, knownfiles, allprocessids, resultverbosity)


                    if fileop == RENAME:
                        dst_file = ev[DST_FILE_NAME]
                        self._find_files_for_file_(dst_file, prefixtext, prefixkey, ev, pair, knownfiles, allprocessids, resultverbosity)

            events_toread -=1


        if resultverbosity == 69:
            filescomment = " "
        else:
            filescomment = " (only first access listed) "


        procs = " ".join(map(str,sorted(allprocessids)))
        if len(allprocessids)<9:
            # (12+len(pair[PAIR][0]))
            print(rt.setfg(CDARKGREEN),
                  " "*(4)+"found", len(knownfiles), "files"+filescomment+"in", len(allprocessids), "executions:",
                  rt.setfg(CLIGHTGREEN), procs)
        else:
            print(rt.setfg(CDARKGREEN),
                  " "*(4)+"found", len(knownfiles), "files"+filescomment+"in", len(allprocessids), "executions:",
                  rt.setfg(CLIGHTGREEN), "first exe:", sorted(allprocessids)[0],
                                         " ... last exe:"+rt.setfg(CLIGHTGREEN), sorted(allprocessids)[-1] )



    def _suspicioustype_to_col(self,pair) -> str:
        if pair[EVAL_TYPE] == TSAME_ASYM or (pair[EVAL_TYPE] == TFUZ_ASYM):
            typecol = rt.setfg(CORANGE)
        elif pair[EVAL_TYPE] == TUNIQUE:
            typecol = rt.setfg(CLIGHTRED)
        else:
            typecol = ""

        return typecol


    def pretty_print_for_humans(self, resultverbosity):
        same_asym  = []
        fuz_asym   = []
        unique     = []
        allpairs_relation = []     # [ (par,child) ]
        allpairs_pairs = {}        #   (par,child) -> pair
        allpairs_prefixes = {}     #   (par,child) -> [ (prefixkeytupl, count, prefixintext) ]

        for looppair in sorted(self.pairs_same):
            pair = self.pairs_same[looppair]
            if pair[EVAL_TYPE] == TSAME_ASYM:
                same_asym.append(looppair)
                allpairs_relation.append(looppair)
                allpairs_pairs[looppair] = pair
                allpairs_prefixes[looppair] = self.find_asym_prefixes(pair)

        for looppair in sorted(self.pairs_var):
            pair = self.pairs_var[looppair]
            if pair[EVAL_TYPE] == TFUZ_ASYM:
                fuz_asym.append(looppair)
                allpairs_relation.append(looppair)
                allpairs_pairs[looppair] = pair
                allpairs_prefixes[looppair] = self.find_asym_prefixes(pair)
            elif pair[EVAL_TYPE] == TUNIQUE:
                unique.append(looppair)
                allpairs_relation.append(looppair)
                allpairs_pairs[looppair] = pair
                allpairs_prefixes[looppair] = self.find_asym_prefixes(pair)

        if len(same_asym)==0 and len(fuz_asym)==0 and len(unique)==0:
            if not self.quiet:
                print("nothing interesting here")
            return

        if not self.quiet:
            print("same:", len(self.pairs_same),
                  "var:", len(self.pairs_var), "and there are ",
                  "SAME_ASYM:", len(same_asym),
                  " FUZ_ASYM:", len(fuz_asym),
                  " UNIQUE:", len(unique) )


        if resultverbosity>59 and resultverbosity<70:
            pairrelsbyfirstevent = sorted(allpairs_relation, key= lambda bla: int(allpairs_pairs[bla][FIRST_EVENT]) )

            print("Pair first seen:         datetime    eventID   parent.exe ===> child.exe      x pair executions")
            for looppair in pairrelsbyfirstevent:
                pair = allpairs_pairs[looppair]

                typecol = self._suspicioustype_to_col(pair)

                print(rt.setfg(CDARK), str(pair[FIRST_TIME])+" ",
                      rt.setfg(CNORM), str(pair[FIRST_EVENT])+" ",
                      rt.setfg(CDARK), pair[PAIR][0],
                      rt.setfg(CNORM), "===>", typecol, pair[PAIR][1],
                      rt.setfg(CDARK), "x"+str(len(pair[EXECS])), rt.resetfg() )

#                prefixes = self.find_asym_prefixes(pair)   # -> [ (prefixkeytupl, count, prefixintext) ]
                prefixes = allpairs_prefixes[looppair]

                if len(prefixes)>0:
                    for tupl in prefixes:
                        # (prefix, count)
                        self.find_files_for_prefix(pair, tupl, resultverbosity)

        else:   #  >=70
            # global range
            first_event = None
            last_event = None

            allsections = []
            sections_no_prefix = []

            pairrelsbylastevent = sorted(allpairs_relation, key= \
            lambda bla:  int(allpairs_pairs[bla][LAST_EVENT]) )
#            lambda bla:  int(allpairs_pairs[bla][LAST_EVENT]) if len(allpairs_prefixes[bla])>0 \
#                    else int(allpairs_pairs[bla][FIRST_EVENT]) )

            for looppair in pairrelsbylastevent:
                pair = allpairs_pairs[looppair]
                # find global range
                if not first_event:
                    first_event = pair[FIRST_EVENT]
                else:
                    first_event = min(first_event, pair[FIRST_EVENT])

                if not last_event:
                    last_event = pair[LAST_EVENT]
                else:
                    last_event = max(last_event, pair[LAST_EVENT])

                # get all unknown prefixes
                prefixes = allpairs_prefixes[looppair]

                if len(prefixes)>0:
                    #                                           2   3minexeid   4   5files  6exeids 7unfiles
                    allsections.append(
                        [pair[FIRST_EVENT], pair[LAST_EVENT], pair, None, prefixes, [],   set(),  set()] )
                else:
                    sections_no_prefix.append(
                        [pair[FIRST_EVENT], pair[LAST_EVENT], pair, None,   None,   [],   set(),  set()] )

#            print("second database search for details in range:", first_event, "-->", last_event)
#            print("")
#            pprint(self.ranges_consumed)
#            for section in allsections:
#                print("SECTION:", section[0], section[1], "---", len(section[4]) )
            if len(allsections)>0:
                donesections = self.find_files_for_all_sections(first_event, last_event, allsections)
            else:
                donesections = []

            for section in sections_no_prefix:
                donesections.append(section)

            for onesection in donesections:
                # has execs from file events (and not only fake network events)
                if onesection[4] and len(onesection[6])>0:
                    onesection[3] = min(onesection[6])

                else:     # no file events, so find our own executions from pair data
                    pair = onesection[2]
                    for tupl in pair[EXECS]:
                        onesection[6].add(tupl[2])

                    onesection[3] = min(onesection[6])

            # sort by minexeid and print process stats
            for onesection in sorted(donesections, key = lambda bla: bla[3]):
                pair = onesection[2]
                typecol = self._suspicioustype_to_col(pair)
                files = onesection[5]
                onesection[6] = list(sorted(onesection[6]))
                execs = onesection[6]
                uniquefiles = onesection[7]

                if resultverbosity!=72:
                    print("    ", onesection[3],
                          rt.setfg(CDARK), pair[PAIR][0],
                          rt.setfg(CNORM), "===>",
                          typecol,         pair[PAIR][1],
                          rt.setfg(CDARK), str(len(execs))+" of "+str(len(pair[EXECS])), "exes,",
                                           str(len(uniquefiles))+" uniq of "+str(len(files)), "file accesses", rt.resetfg() )

                    prefixes = onesection[4]
                    if prefixes:
                        for tupl in prefixes:
                            print(" "*(18),  #+len(pair[PAIR][0])),      # 53
                                  rt.setfg(CTURQ), tupl[2],
                                  rt.setfg(CDARK), " x"+str(tupl[1]),
                                  rt.resetfg() )

                onesection[7] = set()  # clear unique files for later

            if resultverbosity>70:
                self._print_detailed_file_accesses_(donesections, first_event, last_event)


    def _print_detailed_file_accesses_(self, donesections, first_event, last_event):
        i = first_event
#        print("details for", first_event, "-", last_event)

        localranges = deepcopy(self.ranges_consumed)
        seenprocs = set()

        if localranges[0][0]>i:
            i = localranges[0][0]

        iocdata = dict()

        while i<=last_event:

            for onesection in donesections:

                # process events
                while len(onesection[6])>0 and onesection[6][0]<=i:  # lower ones or exactly this one
                    processid = onesection[6][0]
                    if processid not in seenprocs:
                        seenprocs.add(processid)
                        pair = onesection[2]
                        typecol = self._suspicioustype_to_col(pair)

                        procevent = self._get_process_from_database(str(processid))

                        print(
                               rt.setfg(CTURQ), str(processid),
                               rt.setfg(CDARK), pair[PAIR][0]+rt.setfg(CDARK)+'('+str(procevent[PARENT_ID])+')',
                               rt.setfg(CNORM)+"==>"+typecol,
                               pair[PAIR][1]+rt.setfg(CDARK)+'('+str(procevent[ID])+')',
                               rt.setfg(CTURQ)+Filter.remove_leading_binary_name(procevent[COMMAND_LINE]),
                               "",
                               rt.setfg(COFFYELLOW), procevent[WORKING_DIRECTORY],
#                                   rt.setfg(CVIO3), procevent[DOMAIN_NAME],
#                                   rt.setfg(CVIO1), procevent[USER_NAME],
                               rt.resetfg() )

                        if self.ioc:
                            if pair[EVAL_TYPE] == TUNIQUE:
                                entry = (str(processid), "UNIQ process start")
                            else:
                                entry = (str(processid), "ASYM behaving process start")

                            if entry not in iocdata:
                                iocdata[entry] = []

                    onesection[6].pop(0)

                # file events
                if not self.processonly:
                    if len(onesection[5])>0:   # there are files accesses
                        if onesection[5][0][0]==i:   # and this specific one is it
                            uniquefiles = onesection[7]
                            access = onesection[5][0]

                            fullfilename = access[2][0]+access[2][1]+access[2][2]

                            if self.allfiles or (fullfilename not in uniquefiles):
                                pair = onesection[2]
                                typecol = self._suspicioustype_to_col(pair)
                                files = onesection[5]
                                procs = onesection[6]

                                ev = access[1]

                                print(
                                       rt.setfg(CNORM), str(ev[ID]),
                                       rt.setfg(CDARK), pair[PAIR][0]+rt.setfg(CDARK)+'('+str(ev[GRANDPARENT_ID])+')',
                                       rt.setfg(CNORM)+"==>"+typecol,
                                       pair[PAIR][1]+rt.setfg(CDARK)+'('+str(ev[PARENT_ID])+')',
                                       rt.setfg(CNORM)+"-->",
                                       rt.setfg(CLIGHTGREEN) + FILEOP2STR[ev[TYPE]],
                                       rt.setfg(CDARK)      + access[2][0]+ \
                                       rt.setfg(CDARKGREEN) + access[2][1]+ \
                                       rt.setfg(CNORM)      + access[2][2],
                                       rt.resetfg() )

                                uniquefiles.add(fullfilename)

                                if self.ioc:
                                    if pair[EVAL_TYPE] == TUNIQUE:
                                        entry = (str(ev[ID]), "file access of UNIQ process")
                                    else:
                                        entry = (str(ev[ID]), "ASYM file access of known process")

                                    par = str(ev[PARENT_ID])

                                    wasfound = False

                                    for k,v in iocdata.items():
                                        if k[0] == par:
                                            v.append(entry)
                                            wasfound = True
                                            break

                                    if not wasfound:
                                        print("BUG? could not insert file event:", entry[0], entry[1])


                            onesection[5].pop(0)
                            if len(onesection[5])>0:
                                if onesection[5][0][0]==i:  # same id again -> there is a second part of rename
                                    i -=1                   # so cheat and reuse event id
                            break

            i +=1
            if i>localranges[0][1]:
                localranges.pop(0)
                if len(localranges)>0:   # not sure if this extra check is needed
#                    print("fast-forward", i, "to", localranges[0][0])
                    i = localranges[0][0]

        if self.ioc:
#            for proc in iocdata:
#                print("PROC:", proc[0], proc[1])   # eventid, comment
#                for file in iocdata[proc]:
#                    print("     ", file[0], file[1])   # eventid, comment

            self.ioc.mark_ioc(iocdata)



    @staticmethod
    def dump_current_states(inpairs_same, inpairs_var, inreboots : list):

        same_ident = []
        same_sym   = []
        same_asym  = []

        for looppair in sorted(inpairs_same):
            pair = inpairs_same[looppair]
            if pair[EVAL_TYPE] == TSAME_IDENT:
                same_ident.append(looppair)
            elif pair[EVAL_TYPE] == TSAME_SYM:
                same_sym.append(looppair)
            elif pair[EVAL_TYPE] == TSAME_ASYM:
                same_asym.append(looppair)

        ModelCmp4b.sort_and_print_pairs_by_state(same_ident, inpairs_same)
        ModelCmp4b.sort_and_print_pairs_by_state(same_sym, inpairs_same)
        print(rt.setfg(COFFYELLOW)+"--- SAME_ASYM ---")
        ModelCmp4b.sort_and_print_pairs_by_time(same_asym, inpairs_same, inreboots)

        print(rt.setfg(COFFYELLOW)+"--- FUZ* ---")
        ModelCmp4b.sort_and_print_pairs_by_time(inpairs_var.keys(), inpairs_var, inreboots)

    @staticmethod
    def get_pair_data(pair):
        if pair[EVAL_TYPE] != TUNIQUE:
            return (pair[FIRST_EVENT], pair[EVAL_TYPE],
            len(pair[MYDIR_PREFIX]),
            pair[EVAL_STATE][0],
            pair[EVAL_STATE][1],
            pair[PAIR][0],
            pair[PAIR][1],
            len(pair[EXECS]))
        else:
            return (pair[FIRST_EVENT], pair[EVAL_TYPE],
            len(pair[MYDIR_PREFIX]),
            -1,
            -1,
            pair[PAIR][0],
            pair[PAIR][1],
            len(pair[EXECS]))

    def find_pairs_of_type(self, intypes: list) -> list:
        resultlist = []
        for looppair in self.pairs_same:
            pair = self.pairs_same[looppair]
            if pair[EVAL_TYPE] in intypes:
                resultlist.append(ModelCmp4b.get_pair_data(pair))

        for looppair in self.pairs_var:
            pair = self.pairs_var[looppair]
            if pair[EVAL_TYPE] in intypes:
                resultlist.append(ModelCmp4b.get_pair_data(pair))

#        for pair in resultlist:
#            print(pair[FIRST_EVENT], pair[EVAL_TYPE],
#                  pair[PAIR][0], "===>", pair[PAIR][1] )

        return resultlist

###############################################################################

    @staticmethod
    def common_tuple_prefix(a,b):
        i=0
        while i<len(a) and i<len(b) and a[i]==b[i]:
            i+=1
        return a[:i]

    @staticmethod
    def decrease_prefix(store, prefix):
#        print("++", store)
        if store[prefix][()]==1:
            store[prefix].pop( () )
        else:
            store[prefix][()] -= 1
#        print("--", store)


    @staticmethod
    def find_me_a_nil_friend(mystore, otherstore, myprefix,
                            mynilhash, othernilhash, mybin_tupl, otherbin_tupl):
        matchprefix = None
        for testprefix in otherstore:
            matchprefix = ModelCmp4b.common_tuple_prefix(myprefix, testprefix)
            if matchprefix:
                break

        if matchprefix:
            wasprefix = None
            print("    my", rt.setfg(CVIO3), myprefix, rt.resetfg())
            print(" other", rt.setfg(CVIO2), testprefix, rt.resetfg())
            print(" ---->", "",              matchprefix)

            if len(matchprefix)<len(myprefix):
                locstore = deepcopy(mystore)
                ModelCmp4b.add_prefix(locstore, matchprefix)
                ModelCmp4b.decrease_prefix(locstore, matchprefix)
                locnils = {}
                ModelCmp4b.calc_one_nilsimsa(locstore, locnils, mybin_tupl)
                print("   my old", rt.setfg(CVIO3), sorted(mystore[myprefix]), rt.resetfg())
                print("   my new", rt.setfg(CVIO3), sorted(locstore[matchprefix]), rt.resetfg())
                wasprefix = "M\\"+"\\".join(matchprefix)
            else:
                locstore = mystore
                locnils = mynilhash

            if len(matchprefix)<len(testprefix):
                ostore = deepcopy(otherstore)
                ModelCmp4b.add_prefix(ostore, matchprefix)
                ModelCmp4b.decrease_prefix(ostore, matchprefix)
                onils = {}
                ModelCmp4b.calc_one_nilsimsa(ostore, onils, otherbin_tupl)
                print("other old", rt.setfg(CVIO2), sorted(otherstore[testprefix]), rt.resetfg())
                print("other new", rt.setfg(CVIO2), sorted(ostore[matchprefix]), rt.resetfg())
                wasprefix = "O\\"+"\\".join(testprefix)
            else:
                ostore = otherstore
                onils = othernilhash

            newdistance = 128-compare_digests(locnils[matchprefix].hexdigest(),
                                                onils[matchprefix].hexdigest())

            print("    ", rt.setfg(CVIO3), locnils[matchprefix].hexdigest(),  sorted(locstore[matchprefix]), rt.resetfg())
            print("       ", str( newdistance))
            print("    ", rt.setfg(CVIO2),    onils[matchprefix].hexdigest(),  sorted(ostore[matchprefix]), rt.resetfg() )
            return (wasprefix, "\\".join(matchprefix), newdistance)
        else:
            return None
