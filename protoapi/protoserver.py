from protoapi.moduleapi2 import ModuleApi2
from util.config import Config

import protoapi.api_pb2 as pb

class Protoserver:

    def __init__(self, **kwargs):
        self.api = ModuleApi2()

    def reinit(self, req:pb.Request) -> pb.Response:
        self.api.reinit()         # shutdown current instance
        self.api = ModuleApi2()   # instantiate new_one (and hope the garbage collect cleans up)

        res = pb.Response()
        res.command = pb.REINIT
        return res

    def getversion(self, req:pb.Request) -> pb.Response:
        i = req.getversion.data
        res = pb.Response()
        res.command = pb.GETVERSION
        res.getversion.data = Config.get_python_version()
        return res


    def connect(self, req:pb.Request) -> pb.Response:
        apires = self.api.connect(req.connect.model,
                                  req.connect.urldb1, req.connect.hostid1,
                                  req.connect.urldb2, req.connect.hostid2)
        res = pb.Response()
        res.command = pb.CONNECT
        res.connect.events1, res.connect.events2 = apires
        return res

    def consume(self, req:pb.Request) -> pb.Response:
        apires = self.api.consume(req.consume.from1, req.consume.to1,
                                  req.consume.from2, req.consume.to2)
        res = pb.Response()
        res.command = pb.CONSUME
        res.consume.events1, res.consume.events2 = apires
        return res

    def run_evaluation(self, req:pb.Request) -> pb.Response:
        apires = self.api.run_evaluation(req.runevaluation.host)

        res = pb.Response()
        res.command = pb.RUNEVALUATION
        return res


    def get_pair_states_count(self, req:pb.Request) -> pb.Response:
        apires = self.api.get_pair_states_count(req.getpairstatescount.host)
        #(same_ident, same_sym, same_asym, fuz_ident, fuz_sym, fuz_asym, unique)
        res = pb.Response()
        res.command = pb.GETPAIRSTATESCOUNT
        res.getpairstatescount.same_ident = apires[0]
        res.getpairstatescount.same_sym   = apires[1]
        res.getpairstatescount.same_asym  = apires[2]
        res.getpairstatescount.fuz_ident = apires[3]
        res.getpairstatescount.fuz_sym   = apires[4]
        res.getpairstatescount.fuz_asym  = apires[5]
        res.getpairstatescount.unique = apires[6]
        return res


    def get_pairs(self, req:pb.Request) -> pb.Response:
        apires = self.api.get_pairs(req.getpairs.host, list(req.getpairs.type))
        # tuple = (first_event_id, type, prefixes, unmatched_prefixes, hast_distance, parent, child, executions)
        #         (           int,  str,      int,                int,           int,    str,   str,        int)

        res = pb.Response()
        res.command = pb.GETPAIRS

        for thisone in apires:
            item = res.getpairs.entry.add()
            item.eventid         = thisone[0]
            item.type            = thisone[1]
            item.total_prefixes  = thisone[2]
            item.unique_prefixes = thisone[3]
            item.hash_dist       = thisone[4]
            item.parent          = thisone[5]
            item.child           = thisone[6]
            item.execs           = thisone[7]

        return res

###############################################################################

    known_commands = {pb.GETVERSION: getversion,
                      pb.REINIT:     reinit,
                      pb.CONNECT:    connect,
                      pb.CONSUME:    consume,
                      pb.RUNEVALUATION:      run_evaluation,
                      pb.GETPAIRSTATESCOUNT: get_pair_states_count,
                      pb.GETPAIRS:           get_pairs,
                     }

    def parse_and_execute(self, input: bytes) -> bytes:
        req = pb.Request.FromString(input)
        if req.command in Protoserver.known_commands:
            res = Protoserver.known_commands[req.command](self,req)
            return res.SerializeToString()
        else:
            print("BUG! unknown command:", req.command)
            exit(1)
