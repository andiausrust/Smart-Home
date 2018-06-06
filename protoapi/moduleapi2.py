from cybertrap.database import Database
from cybertrap.database_reader4 import DatabaseReader4
from r4.model_cmp4b import ModelCmp4b
from r4.modelconst import TSAME_IDENT, TSAME_SYM, TSAME_ASYM, TFUZ_IDENT, \
    TFUZ_SYM, TFUZ_ASYM, TUNIQUE
from r4.runsql4 import RunSQL4


class ModuleApi2:
    from protoapi.api_pb2 import SAME_IDENT, SAME_SYM, SAME_ASYM, \
                               FUZ_IDENT, FUZ_SYM, FUZ_ASYM, UNIQUE

    def __init__(self, **kwargs):    # traces,
        self.db1 = None
        self.db2 = None

        self.dr1 = None
        self.dr2 = None

        self.model1 = None
        self.model2 = None
        self.run = None

    def reinit(self):
        self.db1.shutdown()
        self.db2.shutdown()
        self.db1 = None
        self.db2 = None

        self.dr1 = None
        self.dr2 = None

        self.model1 = None
        self.model2 = None
        self.run = None
        print("API: reinit cleanup performed")


    # setup a new one
    # connect to two databases with specific hosts
    def connect(self, model: str,
                      database_url1: str,  host1: int,
                      database_url2: str,  host2: int) -> (int,int):

        print("--------------------------------")
        print("API: new CONNECTion")
        self.db1 = Database(database_url1)
        self.db1.print_statistics()

        self.db2 = Database(database_url2)
        self.db2.print_statistics()

        self.dr1 = DatabaseReader4(self.db1, str(host1) )
        self.dr2 = DatabaseReader4(self.db2, str(host2) )

        # model is always "cmp4b"
        # so NOP this for now :-)
        #                           hostid    hostname        colors    dr
        self.model1 = ModelCmp4b(str(host1), "fixmehostname", [11,149], self.dr1)   # hostid, name
        self.model2 = ModelCmp4b(str(host2), "fixmehostname", [14,36],  self.dr2)   # hostid, name

        self.model1.set_other(self.model2)
        self.model2.set_other(self.model1)


        self.run = RunSQL4(self.dr1, self.dr2, True)

        # counting available events from database is expensive,
        # we shouldn't do this in production
        events1 = self.db1.get_count_of_host_event(str(host1))
        events2 = self.db1.get_count_of_host_event(str(host2))

        print('API: events count:', events1, events2)
        return (events1, events2)


    # consume events on stream 1 and stream 2,
    # return number of events actually processed
    #  from 0 to 0 is a NOP
    def consume(self, from_event1: int, to_event1: int,
                      from_event2: int, to_event2: int) -> (int,int):

        # FIXME
        # what to do if one host has no new events? -> implement NO-OP

        events1, events2 = self.run.run_events(self.model1, self.model2,
                                               (from_event1, to_event1),
                                               (from_event2, to_event2))

        print("API: consumed:", events1, events2)
        return (events1, events2)


    # run pairs evaluation
    def run_evaluation(self, host: int):
        if host==1:
            model = self.model1
        elif host==2:
            model = self.model2
        else:
            print("BUG! run_evaluation: host is:", host)
            exit(1)

        model.do_evaluation()


    # get number of pairs in a certain state
    # returned tuple is 7 integers:
    # (same_ident, same_sym, same_asym, fuz_ident, fuz_sym, fuz_asym, unique)
    #
    # this is only fully correct if run_evaluation has been called
    # before this function and no additional events were consumed afterwards
    def get_pair_states_count(self, host: int) -> ():
        states = None

        if host==1:
            states = self.model1.do_count_pair_types()
        elif host==2:
            states = self.model2.do_count_pair_types()
        else:
            print("BUG! count_pair_states: host is:", host)
            exit(1)

        return states

    # get pairs in specific states
    # intypes is array of type constants
    #
    # return array of tuples
    # tuple = (first_event_id, type, prefixes, unmatched_prefixes, hast_distance, parent, child, executions)
    #         (           int,  str,      int,                int,           int,    str,   str,        int)
    def get_pairs(self, host: int,
                     intypes: list):
        if host==1:
            model = self.model1
        elif host==2:
            model = self.model2
        else:
            print("BUG! get_pairs: host is:", host)
            exit(1)

        findtypes = []
        for thistype in intypes:
            findtypes.append( ModuleApi2._convert_api_type_to_internal_type(thistype))

        result = model.find_pairs_of_type(findtypes)

        temp = []
        for thisone in result:
            temp.append( (thisone[0],
                         ModuleApi2._convert_internal_type_to_api_type_(thisone[1]),
                         thisone[2], thisone[3], thisone[4], thisone[5], thisone[6], thisone[7]) )
        print('API: get_pairs: got:', len(result))

#        return None
        return temp

    @staticmethod
    def _convert_api_type_to_internal_type(thistype):
            if thistype == ModuleApi2.SAME_IDENT:
                return TSAME_IDENT
            elif thistype == ModuleApi2.SAME_SYM:
                return TSAME_SYM
            elif thistype == ModuleApi2.SAME_ASYM:
                return TSAME_ASYM
            elif thistype == ModuleApi2.FUZ_IDENT:
                return TFUZ_IDENT
            elif thistype == ModuleApi2.FUZ_SYM:
                return TFUZ_SYM
            elif thistype == ModuleApi2.FUZ_ASYM:
                return TFUZ_ASYM
            elif thistype == ModuleApi2.UNIQUE:
                return TUNIQUE
            else:
                print("BUG! convert_api_type_to_internal_type: unknown type:", thistype)
                exit(1)

    @staticmethod
    def _convert_internal_type_to_api_type_(thisone):
        if thisone == TSAME_IDENT:
            return ModuleApi2.SAME_IDENT
        elif thisone == TSAME_SYM:
            return ModuleApi2.SAME_SYM
        elif thisone == TSAME_ASYM:
            return ModuleApi2.SAME_ASYM
        if thisone == TFUZ_IDENT:
            return ModuleApi2.FUZ_IDENT
        elif thisone == TFUZ_SYM:
            return ModuleApi2.FUZ_SYM
        elif thisone == TFUZ_ASYM:
            return ModuleApi2.FUZ_ASYM
        elif thisone == TUNIQUE:
            return ModuleApi2.UNIQUE
        else:
            print("BUG! convert_internal_type_to_api_type: unknown type:", thisone)
            exit(1)

