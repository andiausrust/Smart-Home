import datetime as dt
from collections import OrderedDict
from datetime import timedelta
from pprint import pprint

from cybertrap.database_reader4 import DatabaseReader4
from cybertrap.filter import Filter
from r4.modeltemplate import ModelTemplate
from r4.modelconst import *

from cybertrap.dbconst import *

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

class ModelCmp4(ModelTemplate):
    def get_modelname(self):
        return "CMP4"

    def __init__(self, hostid :str,
                       name   :str,
                       colors :list,
                           dr :DatabaseReader4, **kwargs):

        self.hostid     = hostid
        self.hostname   = name
        self.hostnameid = name+"/"+hostid

        self.hostcolhi, self.hostcollo = colors

        self.clear_state()
        self.last_event_consumed = None

        self.other  = None
        self.reboots = []
        self.rebootid  = None   # event id of last seen reboot as int
        self.rebootstr = None   # as string
        self.time_first_reboot = None   # time of first reboot

        self.tick_start = None
        self.tick_end = None
        self.tick_delta   = timedelta(seconds=60) * 60*3    # ticker for model internal periodic tasks


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

    def get_uniqueness_state(self, timetick: dt.datetime) -> dict:

        result = dict()

        same_ident = 0
        same_sym   = 0
        same_asym_ok  = 0
        same_asym_uni  = 0
        fuz_sym  = 0
        fuz_asym = 0
        fuz_uni  = 0
        whatelse = 0

        for looppair in self.pairs_same:
            pair = self.pairs_same[looppair]
            if pair[EVAL_TYPE] == TSAME_IDENT:
                same_ident +=1
            elif pair[EVAL_TYPE] == TSAME_SYM:
                same_sym +=1
            elif pair[EVAL_TYPE] == TSAME_ASYM_OK:
                same_asym_ok +=1
            elif pair[EVAL_TYPE] == TSAME_ASYM_UNI:
                same_asym_uni +=1
            else:
                print(pair[PAIR][0],"==>",pair[PAIR][1], " ", pair[LAST_EVENT], pair[EVAL_EVENT], pair[EVAL_TYPE])
                whatelse += 1

        for looppair in self.pairs_var:
            pair = self.pairs_var[looppair]
            if pair[EVAL_TYPE] == TFUZ_SYM:
                fuz_sym +=1
            elif pair[EVAL_TYPE] == TFUZ_ASYM:
                fuz_asym +=1
            elif pair[EVAL_TYPE] == TUNIQUE:
                fuz_uni +=1

        result['state_same_ident'] = same_ident
        result['state_same_sym']   = same_sym
        result['state_same_asym_ok']   = same_asym_ok
        result['state_same_asym_uni']  = same_asym_uni

#        result['state_var_fuz_sym']  = fuz_sym
#        result['state_var_fuz_asym'] = fuz_asym
        result['state_var_uni']  = len(self.pairs_var) #fuz_uni

        all = (same_ident+same_sym+same_asym_ok)+(same_asym_uni+result['state_var_uni'])
        result['percent_100%'] = 1.0
        result['percent_ok' ]  = (same_ident+same_sym+same_asym_ok) / all
        result['percent_uni' ] = (same_asym_uni+result['state_var_uni']) / all

        # print(rt.setfg(self.hostcolhi),
        #       str(len(self.pairs_same)).rjust(2),
        #       str(len(self.pairs_var)).rjust(2)," ",
        #
        #       str(same_ident).rjust(2)+"sI",
        #       str(same_sym).rjust(2)+"sS",
        #       str(same_asym_ok).rjust(2)+"sAO", "",
        #       str(same_asym_uni).rjust(2)+"saI","   ",
        #       str(len(self.pairs_var)).rjust(2)+"F","  ",
        #       str(whatelse).rjust(2)+"?",
        #       rt.resetfg() )

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
    def _nilsimsa_distance_(indigest1, indigest2):
        return (128-compare_digests(indigest1, indigest2))

##############################################################################

    def consume_process(self, ev):
        evid        = int(ev[ID])
        timestamp   = ev[TIME]
        binary      = ev[PROCESS_NAME]

        cmd_line          = ev[COMMAND_LINE]
        user_name         = ev[USER_NAME]
        domain_name       = ev[DOMAIN_NAME]
#       working_directory = ev[WORKING_DIRECTORY]   # ignore

        parent_binary = ev[PARENT_PROCESS_NAME]
        parent_id     = ev[PARENT_ID]


        if parent_id is None:
            # print("P", evid, "parent is None, so I must be the reboot process event")
            # so parent_id==None, too
            parent_binary = r"\REBOOT"
            if int(ev[ID]) != self.rebootid:
                print("BUG?", evid, "parent is None, but my last rebootid is", self.rebootid)
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

            if parent_id is None:  # we have no parent, so surely no grandparent info
                parent_id = -1
                grandp_id = -1
                gpppair = None
                gpexec = (-1,-1, parent_id,timestamp)
            else:  # find our grandparent
                gpppair, gpexec = self.find_parent_pair(parent_id, relation[0])
                if gpppair:
                    grandp_id = gpexec[1]
                else:
                    grandp_id = -1
                    gpppair = None

            if item:
                item[EXECS].append((grandp_id,parent_id,evid,timestamp))
                item[LAST_TIME] = timestamp
                item[LAST_EVENT] = evid
            else:
                # new to me, so instantiate a new entry
                item = self.instantiate_pair(relation,evid,timestamp,parent_id, grandp_id)
                self.save_pair_dict(relation, item, evid, timestamp, gpppair)

            if grandp_id != -1:
                if gpppair[PAIR] not in item[PARENT_PAIR]:
                    item[PARENT_PAIR][gpppair[PAIR]] =     [ (gpppair, grandp_id,parent_id) ]
                else:
                    item[PARENT_PAIR][gpppair[PAIR]].append( (gpppair, grandp_id,parent_id) )

        else:
#            pass
            print(evid, binary, " has no parent :-(")


    def _find_execution_of_binary_(self, evid, binary, inpairs):
        parentpair = None
        for looppair in inpairs:
            pair = inpairs[looppair]

            if pair[PAIR][1]==binary:
                if pair[FIRST_EVENT] <= evid and \
                   evid <= pair[LAST_EVENT]:
                        for entry in pair[EXECS]:
                           if entry[2]==evid:
                               parentpair = (pair, entry)
                               break
        return parentpair


    def find_parent_pair(self, parent_id, child_binary):
        parentpair = self._find_execution_of_binary_(parent_id, child_binary, self.pairs_same)
        if not parentpair:
            parentpair = self._find_execution_of_binary_(parent_id, child_binary, self.pairs_var)
        return parentpair


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
        item[EVAL_TYPE]  = None
        item[EVAL_STATE] = None

        return item



    def save_pair_dict(self, relation, item, evid, timestamp, gpppair):
            # insert pair data structure into active sets
            # called either a) for brand new pair or b) for resurrection of expired pair

            if relation in self.other.pairs_var:
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

                here_friend = item_other[FRIEND]
                if here_friend is not None:
                    # if other had a friend here already, it must be a fuzzy matched friend
                    # we have to divorce them, same-ness is better
                    here_friend[FRIEND] = None
                    print("FIXME! BUG! var has friend!")
                    exit(1)

                # forge a stable bond as same friends forever
                item[FRIEND]       = item_other
                item_other[FRIEND] = item

                grandparent = ""
                if gpppair:
                    grandparent = gpppair[PAIR][0]
#                    print( rt.setfg(CDARK), item[PARENT_PAIR][PAIR][0], rt.resetfg(), " ===> ",
#                           rt.setfg(CDARK), item[PARENT_PAIR][PAIR][1], rt.resetfg() )

                print(rt.setfg(self.hostcollo), str(len(self.pairs_same)).rjust(2), str(len(self.pairs_var)).rjust(2),
                      rt.setfg(CDARK), "  -:", self.hostid, evid, timestamp,
                      rt.setfg(CDARKBLUE), grandparent, rt.resetfg(), "===>",
                      rt.setfg(CNORM), relation[0], rt.resetfg(), "===>",
                      rt.setfg(CNORM), relation[1], rt.resetfg())

            else:
                grandparent = ""
                if gpppair:
                    grandparent = gpppair[PAIR][0]

#                if item[PARENT_PAIR]:
#                    print( rt.setfg(CDARK), item[PARENT_PAIR][PAIR][0], rt.resetfg(), " ===> ",
#                           rt.setfg(CDARK), item[PARENT_PAIR][PAIR][1], rt.resetfg() )

                # new to us and also unknown to other
                # so just save, until we have some additional events to find a friend,
                self.pairs_var[relation] = item
                print(rt.setfg(self.hostcolhi), str(len(self.pairs_same)).rjust(2), str(len(self.pairs_var)).rjust(2),
                      rt.setfg(CNORM), " + :", self.hostid, evid, timestamp,
                      rt.setfg(CDARKBLUE), grandparent, rt.resetfg(), "===>",
                      rt.setfg(CNORM), relation[0], rt.resetfg(), " ===> ",
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

#        if binary is not parent_binary:
#            print("F", evid, "process_name mismatches parent:  ", parent_binary, "-->", binary)


        if parent_binary is not None:
            relation = (parent_binary, binary)

            item = self.pairs_same.get(relation)

            if not item:
                 item = self.pairs_var.get(relation)

            if not item:
                print(str(evid).rjust(8), "file event with no pair?: ", parent_binary, " ===> ", binary, " ", process_evid, parent_binary)
                exit(1)
                return



            t1_frags_without_file = self._path_to_fragments_without_file(src_file)
#            t1 = tuple(map(len,t1_frags_without_file))

#            print(src_file, "", t1_frags_without_file, "", t1)

            l = len(item[BIN_TUPL_CUT])
            if t1_frags_without_file[:l] == item[BIN_FRAG_CUT]:   # if t1[:l]== binentry[BIN_TUPL_CUT]:
                t1_frags_without_file = ["EXEDIR"]+t1_frags_without_file[l:]
#                t1 = (-99,)+t1[l:]

            # access in root, so rise by one virtual ROOT directory
            if len(t1_frags_without_file)==0:
#                print("S", src_file, evid)
                filename = self._path_to_fragments_with_file(src_file)[-1]
                t1_frags_without_file = ["ROOT"]
#                t1 = (-90,len(filename))

#            print(src_file, "", t1_frags_without_file, "", t1)
            self.add_prefix(item[MYDIR_PREFIX], t1_frags_without_file)


            if fileop == RENAME:
                dst_file = ev[DST_FILE_NAME]

                t2_frags_without_file = self._path_to_fragments_without_file(dst_file)
#                t2 = tuple(map(len,t2_frags_without_file))
#                print(dst_file, "", t2_frags_without_file, "", t2)

                l = len(item[BIN_TUPL_CUT])
                if t2_frags_without_file[:l] == item[BIN_FRAG_CUT]:   # if t2[:l]== binentry[BIN_TUPL_CUT]:
                    t2_frags_without_file = ["EXEDIR"]+t2_frags_without_file[l:]
#                    t2 = (-99,)+t2[l:]

                # access in root, so rise by one virtual ROOT directory
                if len(t2_frags_without_file)==0:
#                    print("D", src_file, evid)
                    filename = self._path_to_fragments_with_file(dst_file)[-1]
                    t2_frags_without_file = ["ROOT"]
#                    t2 = (-90,len(filename))

#                print(dst_file, "", t2_frags_without_file, "", t2)

                self.add_prefix(item[MYDIR_PREFIX], t2_frags_without_file)



            item[LAST_EVENT]  = evid
            item[LAST_TIME]   = timestamp

#            self._add_one_to_key_(item[MYDIR_TUPL], t1)
#            if t2:
#                self._add_one_to_key_(item[MYDIR_TUPL], t2)


##############################################################################

    def consume_event(self, ev: dict):
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


            elif ev[TYPE_ID] == REGISTRY:
                self.total_events_registry +=1
                reg_path = ev[PATH]
                reg_key = ev[KEY]

            elif ev[TYPE_ID] == THREAD:
                self.total_events_thread +=1

            elif ev[TYPE_ID] == NETWORK:
                self.total_events_network +=1

            else:
                print("bug! unknown event type!")
                exit(1)


            if ev[TIME] > self.tick_start:
                self.one_tick(ev)

            self.last_event_consumed = ev


    def one_tick(self, ev):
#        print(">>>TICK:", printNiceTimeDelta(ev[RELTIME]), ev[TIME])
        self.eval_same()
        self.eval_var()
        self.other.eval_same()
        self.other.eval_var()

        self.tick_start = self.tick_end
        self.tick_end = self.tick_start + self.tick_delta

        self.save_state(ev[RELTIME])


    def eval_same(self):
        for looppair in self.pairs_same:
            pair = self.pairs_same[looppair]
            friend = pair[FRIEND]

            # only if new event consumed since last evaluation
            if    (pair[LAST_EVENT] != pair[EVAL_EVENT]) or \
                (friend[LAST_EVENT] != friend[EVAL_EVENT]):
#            if    (pair[LAST_EVENT] != pair[EVAL_EVENT]) or (pair[EVAL_TYPE] is None) or \
#                (friend[LAST_EVENT] != friend[EVAL_EVENT]) or (friend[EVAL_TYPE] is None):

                self.eval_same_pair(pair)


    def eval_var(self):
        for looppair in self.pairs_var:
            pair = self.pairs_var[looppair]

            # only if new event consumed since last evaluation
            if pair[LAST_EVENT] != pair[EVAL_EVENT]:
                # FIXME
                ModelCmp4.calc_one_nilsimsa(pair[MYDIR_PREFIX], pair[MYDIR_PRENIL], pair[BIN_TUPL])
                pair[EVAL_EVENT] = pair[LAST_EVENT]



    @staticmethod
    def eval_prefixes(inpair:dict, infriend:dict) -> tuple:
        missing_prefixes = 0   # number of
        total_dist = 0         # sum of all hash distances
        result = {}
        for testprefix in sorted(inpair[MYDIR_PREFIX]):
            if testprefix in infriend[MYDIR_PREFIX]:
                dist = ModelCmp4._nilsimsa_distance_(inpair[MYDIR_PRENIL][testprefix].hexdigest(),
                                                   infriend[MYDIR_PRENIL][testprefix].hexdigest())
                result[testprefix] = (testprefix, testprefix, dist)
                total_dist += dist
            else:
                # no direct match, maybe via uplifting or approximate matching?
                matchprefix = None

                for otherprefix in infriend[MYDIR_PREFIX]:
                    matchprefix = ModelCmp4.common_tuple_prefix(testprefix, otherprefix)
                    if matchprefix:
                        break

                if matchprefix:
                    result[testprefix] = (testprefix, matchprefix, -1)
                else:
                    missing_prefixes += 1
                    result[testprefix] = None

        return (missing_prefixes, total_dist, result)


    def eval_same_pair(self, pair):
            friend = pair[FRIEND]

            if pair[LAST_EVENT] != pair[EVAL_EVENT]:
                ModelCmp4.calc_one_nilsimsa(pair[MYDIR_PREFIX], pair[MYDIR_PRENIL], pair[BIN_TUPL])

            if friend[LAST_EVENT] != friend[EVAL_EVENT]:
                ModelCmp4.calc_one_nilsimsa(friend[MYDIR_PREFIX], friend[MYDIR_PRENIL], friend[BIN_TUPL])

            myprefixes = set(sorted(pair[MYDIR_PREFIX]))
            otherprefixes = set(sorted(friend[MYDIR_PREFIX]))
            myuniqueprefixes = myprefixes - otherprefixes
#            sharedprefixes = set(myprefixes) & set(otherprefixes)
#            uniqueprefixes = set(myprefixes) ^ set(otherprefixes)

            if len(myuniqueprefixes)==0:
                myhashes    = set(pair[MYDIR_PRENIL].values())
                otherhashes = set(friend[MYDIR_PRENIL].values())
                if myhashes == otherhashes:           # hashes identical
                    pair[EVAL_TYPE] = TSAME_IDENT
                    pair[EVAL_STATE] = (0,0, None)

                else:   # hashes have some distance
                    total_dist = 0
                    result = {}

                    for thisprefix in pair[MYDIR_PREFIX]:
                        dist = ModelCmp4._nilsimsa_distance_(
                            pair  [MYDIR_PRENIL][thisprefix].hexdigest(),
                            friend[MYDIR_PRENIL][thisprefix].hexdigest() )
                        result[thisprefix] = (thisprefix, thisprefix, dist)
                        total_dist += dist

                    pair[EVAL_TYPE] = TSAME_SYM
                    pair[EVAL_STATE] = (0, total_dist, result)
            else:  # I have unique prefixes
                result = self.eval_prefixes(pair, friend)
                pair[EVAL_STATE] = result
                if result[0]>0:
                    pair[EVAL_TYPE] = TSAME_ASYM_UNI
                else:
                    pair[EVAL_TYPE] = TSAME_ASYM_OK

            pair[EVAL_EVENT] = pair[LAST_EVENT]
            # don't update friend[EVAL_EVENT] here, this is done from the other side


    # re-evaluate all friendships of "not same" pairs
    def check_friendships(self):
        pass

##############################################################################


    def print_result(self, result=None):
        if not result:
            return

        result = int(result)

        if result == 0:
            print("supported results:")
            print("21 - unique prefix dirs per host")
            print("30 - raw dump of all prefixes and hashes")
            print("40 - r4 matcher by end of run evaluation")
            print("50 - r4 matcher by periodic tick evaluation")
            pass


        if result == 1:
            print("hello world!")
            pass


        elif result == 21:
            alldirs = {}
            max1 = ModelCmp4.addup_root_dirs(alldirs, self.pairs_same)
            max2 = ModelCmp4.addup_root_dirs(alldirs, self.pairs_var)

            otherdirs = {}
            max3 = ModelCmp4.addup_root_dirs(otherdirs, self.other.pairs_same)
            max4 = ModelCmp4.addup_root_dirs(otherdirs, self.other.pairs_var)


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
            max1 = ModelCmp4.addup_root_dirs(alldirs, self.pairs_same)
            max2 = ModelCmp4.addup_root_dirs(alldirs, self.pairs_var)

            otherdirs = {}
            max3 = ModelCmp4.addup_root_dirs(otherdirs, self.other.pairs_same)
            max4 = ModelCmp4.addup_root_dirs(otherdirs, self.other.pairs_var)

            print("   ||| SAME |||")
            ModelCmp4.dump_prefix_and_nil(self.pairs_same)
            print("   ||| VAR |||")
            ModelCmp4.dump_prefix_and_nil(self.pairs_var)


        elif result == 40:
            ModelCmp4.dump_current_matching(self.pairs_same, self.pairs_var)


        elif result >=50 and result <=59:
            self.eval_same()
            self.eval_var()   # FIXME

            ModelCmp4.dump_current_states(self.pairs_same, self.pairs_var, self.reboots)



##############################################################################


    @staticmethod
    def addup_root_dirs(allprefix, inpairs):
        max_prefixes = 0
        for pair in inpairs:
            p = inpairs[pair]
            if len(p[MYDIR_PREFIX]) > max_prefixes:
                max_prefixes = len(p[MYDIR_PREFIX])
            for prefixkey in p[MYDIR_PREFIX]:
                ModelCmp4._add_one_to_key_(allprefix, prefixkey)
        return max_prefixes



    @staticmethod
    def calc_one_nilsimsa_for_one_prefix(prefix: tuple, prefixdata:dict, bintupl:dict):
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
                n = ModelCmp4.calc_one_nilsimsa_for_one_prefix(prefix, inprefixes[prefix], bintupl)
                nilstore[prefix] = n


    @staticmethod
    def dump_prefix_and_nil(inpairs):
        for looppair in sorted(inpairs):
            pair = inpairs[looppair]

            print(rt.setfg(CVIO3), pair[PAIR][0], rt.setfg(CNORM), "===>",
                  rt.setfg(CVIO3), pair[PAIR][1], rt.resetfg())

            ModelCmp4.calc_one_nilsimsa(pair[MYDIR_PREFIX], pair[MYDIR_PRENIL], pair[BIN_TUPL])
            myprefixes = sorted(pair[MYDIR_PREFIX])
            friend = pair[FRIEND]

            otherprefixes = []
            sharedprefixes = {}
            uniqueprefixes = {}

            if friend:
                ModelCmp4.calc_one_nilsimsa(friend[MYDIR_PREFIX], friend[MYDIR_PRENIL], friend[BIN_TUPL])
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
                #         match = ModelCmp4.find_me_a_nil_friend(pair[MYDIR_PREFIX], friend[MYDIR_PREFIX],
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
    def dump_current_matching(inpairs_same, inpairs_var):
        print("   <<< SAME >>>")

        same_ident = []
        same_sym  = []
        same_asym = []

        for looppair in sorted(inpairs_same):
            pair = inpairs_same[looppair]
            friend = pair[FRIEND]

            ModelCmp4.calc_one_nilsimsa(pair[MYDIR_PREFIX], pair[MYDIR_PRENIL], pair[BIN_TUPL])
            myprefixes = set(sorted(pair[MYDIR_PREFIX]))

#            if friend:  # here always true for same
            ModelCmp4.calc_one_nilsimsa(friend[MYDIR_PREFIX], friend[MYDIR_PRENIL], friend[BIN_TUPL])
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
                            match = ModelCmp4.find_me_a_nil_friend(pair[MYDIR_PREFIX], friend[MYDIR_PREFIX],
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
#        friend = pair[FRIEND]
        myprefixes = set(pair[MYDIR_PREFIX])

        s = pair[EVAL_STATE]

        if s and (s[2] is not None):
            for prefixkey in s[2]:
                if s[2][prefixkey]:
                    col = CLIGHTGREEN
                    dist = s[2][prefixkey][2]    # dist calculated
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
                      rt.setfg(distcol), dist,
                      rt.setfg(col), "  \\"+"\\".join(prefixkey),
                      rt.setfg(CDARK), " x"+str(tupl_count), rt.resetfg() )

        else:
            for prefixkey in myprefixes:
                col = CNORM
                dist = "???"
                tupl_count = 0
                if prefixkey in pair[MYDIR_PRENIL]:
                    nils = pair[MYDIR_PRENIL][prefixkey]
                    for tupl in pair[MYDIR_PREFIX][prefixkey]:
                        tupl_count += pair[MYDIR_PREFIX][prefixkey][tupl]
                else:
                    nils = "----------------------------------------------------------------"


                print("     ",
                      rt.setfg(CDARK), nils,
                      rt.setfg(col), dist,
                      rt.setfg(COFFGREEN), "  \\"+"\\".join(prefixkey),
                      rt.setfg(CDARK), " x"+str(tupl_count), rt.resetfg() )

                #for tupl in sorted(pair[MYDIR_PREFIX][prefixkey]):
                #    print(rt.setfg(CVIO1),"                                                                                " + \
                #         str(tupl)+"  x"+str(pair[MYDIR_PREFIX][prefixkey][tupl]) )


    @staticmethod
    def evaltype2str(ty):
        if ty==TSAME_IDENT:
            return "SAME_IDENT"
        elif ty==TSAME_SYM:
            return "SAME_SYM  "
        elif ty==TSAME_ASYM_OK:
            return "SA_ASY_OK "
        elif ty==TSAME_ASYM_UNI:
            return "SA_ASY_UNI"
        elif ty==TFUZ_SYM:
            return "VAR_SAM   "
        elif ty==TFUZ_ASYM:
            return "VAR_ASYM  "
        elif ty==TUNIQUE:
            return "UNIQUE    "
        else:
            print("help! unknown type?", ty)
            exit(1)


    @staticmethod
    def print_one_pair(inpair):
            pair = inpair
            s = pair[EVAL_STATE]
            if s[0]>0:
                colprefixes = CLIGHTRED
            else:
                colprefixes = CLIGHTGREEN

            if s[1]>0:
                coldist = CLIGHTRED
            else:
                coldist = CLIGHTGREEN

            if (pair[EVAL_TYPE] == TSAME_IDENT) or \
               (pair[EVAL_TYPE] == TSAME_SYM):
                paircol = CLIGHTGREEN
            elif pair[EVAL_TYPE] == TSAME_ASYM_OK:
                paircol = CDARKGREEN
            elif pair[EVAL_TYPE] == TSAME_ASYM_UNI:
                paircol = CLIGHTRED
            else:
                paircol = CVIO3

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
                elif gptype == TSAME_ASYM_OK:
                    colgrand = CDARKGREEN
                elif gptype == TSAME_ASYM_UNI:
                    colgrand = CLIGHTRED
                else:  # bug
                    colgrand = CVIO2


            gpexe, pexe, myexe = ModelCmp4.find_executions(pair)

            print(str(pair[FIRST_EVENT]).rjust(8),
                  rt.setfg(CNORM)+ModelCmp4.evaltype2str(pair[EVAL_TYPE]),
                  rt.setfg(CVIO1),str(len(pair[MYDIR_PREFIX])), " ",
                  rt.setfg(colprefixes),str(s[0])+"|"+
                  rt.setfg(coldist),    str(s[1]).rjust(2), " ",

                  rt.setfg(colgrand), grandparent+gpexe, rt.setfg(CNORM), "===>",
                  rt.setfg(colgrand), pair[PAIR][0]+pexe, rt.setfg(CNORM), "===>",
                  rt.setfg(paircol), pair[PAIR][1]+myexe,
                  rt.setfg(CDARK), "x"+str(len(pair[EXECS])), rt.resetfg())
            ModelCmp4.print_prefixes(pair)

    @staticmethod
    def sort_and_print_pairs_by_state(intuples, inpairs):
        temp = sorted(intuples, key= lambda bla: inpairs[bla][EVAL_STATE][0:2] )
        for looppair in temp:
            pair = inpairs[looppair]
            ModelCmp4.print_one_pair(pair)


    @staticmethod
    def sort_and_print_pairs_by_time(intuples, inpairs, inreboots):
        temp = sorted(intuples, key= lambda bla: int(inpairs[bla][FIRST_EVENT]) )
        reboots = deepcopy(inreboots)

        for looppair in temp:
            pair = inpairs[looppair]

            while reboots and reboots[0]<int(pair[FIRST_EVENT]):
                print(rt.setfg(CTURQ)+str(reboots.pop(0)).rjust(8), "REBOOT", rt.resetfg())

            ModelCmp4.print_one_pair(pair)

        while reboots:
            print(rt.setfg(CTURQ)+str(reboots.pop(0)).rjust(8), "REBOOT", rt.resetfg())


    @staticmethod
    def find_executions(inpair:dict) -> tuple:
        if len(inpair[EXECS])==1:
            myexe = '('+str(inpair[EXECS][0][2])+")"
            parentexe = '('+str(inpair[EXECS][0][1])+')'
            gpexe = '('+str(inpair[EXECS][0][0])+')'
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


    @staticmethod
    def dump_current_states(inpairs_same, inpairs_var, inreboots : list):

        same_ident = []
        same_sym  = []
        same_asym_ok = []
        same_asym_uni = []

        for looppair in sorted(inpairs_same):
            pair = inpairs_same[looppair]
            if pair[EVAL_TYPE] == TSAME_IDENT:
                same_ident.append(looppair)
            elif pair[EVAL_TYPE] == TSAME_SYM:
                same_sym.append(looppair)
            elif pair[EVAL_TYPE] == TSAME_ASYM_OK:
                same_asym_ok.append(looppair)
            elif pair[EVAL_TYPE] == TSAME_ASYM_UNI:
                same_asym_uni.append(looppair)

        ModelCmp4.sort_and_print_pairs_by_state(same_ident, inpairs_same)
        ModelCmp4.sort_and_print_pairs_by_state(same_sym, inpairs_same)
        ModelCmp4.sort_and_print_pairs_by_state(same_asym_ok, inpairs_same)
        print(rt.setfg(COFFYELLOW)+"--- SAME_ASYM_UNI ---")
        ModelCmp4.sort_and_print_pairs_by_time(same_asym_uni, inpairs_same, inreboots)

        print(rt.setfg(COFFYELLOW)+"--- VAR* ---")

        # sorted by time
        temp = sorted(inpairs_var, key= lambda bla: inpairs_var[bla][FIRST_EVENT] )
        reboots = deepcopy(inreboots)

        for looppair in temp:
            pair = inpairs_var[looppair]

            while reboots and reboots[0]<pair[FIRST_EVENT]:
                print(rt.setfg(CTURQ)+str(reboots.pop(0)).rjust(8), "REBOOT", rt.resetfg())


            grandparent = ""
            colgrand = CDARKBLUE

            if len(pair[PARENT_PAIR])==1:
                gptupl = list(pair[PARENT_PAIR].keys()) [0]  # get only tuple key of dict
                gpentry = pair[PARENT_PAIR][gptupl][0]          # get data tuple
                grandparent = gpentry[0] [PAIR][0]
                gptype      = gpentry[0] [EVAL_TYPE]

                if gptype == TSAME_IDENT or gptype == TSAME_SYM:
                    colgrand = CLIGHTGREEN
                elif gptype == TSAME_ASYM_OK:
                    colgrand = CDARKGREEN
                elif gptype == TSAME_ASYM_UNI:
                    colgrand = CLIGHTRED
                else:  # bug
                    colgrand = CVIO2

            gpexe, pexe, myexe = ModelCmp4.find_executions(pair)

            print(str(pair[FIRST_EVENT]).rjust(8),
                  rt.setfg(CNORM)+"VAR_???   ",
                  rt.setfg(CVIO1),str(len(pair[MYDIR_PREFIX])), " ",
                  rt.setfg(CDARKRED),    str("?")+"|"+
                  rt.setfg(CDARKRED),    str("  ?").rjust(2), " ",

                  rt.setfg(colgrand), grandparent+gpexe, rt.setfg(CNORM), "===>",
                  rt.setfg(colgrand), pair[PAIR][0]+pexe, rt.setfg(CNORM), "===>",
                  rt.setfg(CLIGHTRED), pair[PAIR][1]+myexe,
                  rt.setfg(CDARK), "x"+str(len(pair[EXECS])), rt.resetfg())
            ModelCmp4.print_prefixes(pair)

        while reboots:
            print(rt.setfg(CTURQ)+str(reboots.pop(0)).rjust(8), "REBOOT", rt.resetfg())

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
            matchprefix = ModelCmp4.common_tuple_prefix(myprefix, testprefix)
            if matchprefix:
                break

        if matchprefix:
            wasprefix = None
            print("    my", rt.setfg(CVIO3), myprefix, rt.resetfg())
            print(" other", rt.setfg(CVIO2), testprefix, rt.resetfg())
            print(" ---->", "",              matchprefix)

            if len(matchprefix)<len(myprefix):
                locstore = deepcopy(mystore)
                ModelCmp4.add_prefix(locstore, matchprefix)
                ModelCmp4.decrease_prefix(locstore, matchprefix)
                locnils = {}
                ModelCmp4.calc_one_nilsimsa(locstore, locnils, mybin_tupl)
                print("   my old", rt.setfg(CVIO3), sorted(mystore[myprefix]), rt.resetfg())
                print("   my new", rt.setfg(CVIO3), sorted(locstore[matchprefix]), rt.resetfg())
                wasprefix = "M\\"+"\\".join(matchprefix)
            else:
                locstore = mystore
                locnils = mynilhash

            if len(matchprefix)<len(testprefix):
                ostore = deepcopy(otherstore)
                ModelCmp4.add_prefix(ostore, matchprefix)
                ModelCmp4.decrease_prefix(ostore, matchprefix)
                onils = {}
                ModelCmp4.calc_one_nilsimsa(ostore, onils, otherbin_tupl)
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
