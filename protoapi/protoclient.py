from protoapi.moduleapi2 import ModuleApi2
from sys import exit
import protoapi.api_pb2 as pb


class Protoclient(ModuleApi2):

    # pass a helper function send_and_receive(req: bytes) -> bytes:
    def __init__(self, send_and_receive, **kwargs):
        self.send_and_receive = send_and_receive

    def _send_and_check(self, req: pb.Request, expectedtype: int) -> pb.Response:
        by = self.send_and_receive(req.SerializeToString())
        res = pb.Response.FromString(by)

        if res.command != expectedtype:
            print("BUG! expected", expectedtype, "but got:", res.command); exit(1)

        return res

###############################################################################

    def getversion(self, thisone: int) -> str:
        req = pb.Request()
        req.command = pb.GETVERSION
        req.getversion.data = thisone

        res = self._send_and_check(req, pb.GETVERSION)
        return res.getversion.data


    def reinit(self):
        req = pb.Request()
        req.command = pb.REINIT

        res = self._send_and_check(req, pb.REINIT)
        return None


    def connect(self, model: str,
                      database_url1: str,  host1: int,
                      database_url2: str,  host2: int) -> (int,int):

        req = pb.Request()
        req.command = pb.CONNECT
        req.connect.model = model
        req.connect.urldb1  = database_url1
        req.connect.hostid1 = host1
        req.connect.urldb2  = database_url2
        req.connect.hostid2 = host2

        res = self._send_and_check(req, pb.CONNECT)
        return (res.connect.events1, res.connect.events2)


    def consume(self, from_event1: int, to_event1: int,
                      from_event2: int, to_event2: int) -> (int,int):

        req = pb.Request()
        req.command = pb.CONSUME
        req.consume.from1 = from_event1
        req.consume.to1   = to_event1
        req.consume.from2 = from_event2
        req.consume.to2   = to_event2

        res = self._send_and_check(req, pb.CONSUME)
        return (res.consume.events1, res.consume.events2)

    # run pairs evaluation
    def run_evaluation(self, host: int):
        req = pb.Request()
        req.command = pb.RUNEVALUATION
        req.runevaluation.host = host

        res = self._send_and_check(req, pb.RUNEVALUATION)
        return None



    def get_pair_states_count(self, host: int) -> ():
        req = pb.Request()
        req.command = pb.GETPAIRSTATESCOUNT
        req.getpairstatescount.host = host

        res = self._send_and_check(req, pb.GETPAIRSTATESCOUNT)
        return (res.getpairstatescount.same_ident,
                res.getpairstatescount.same_sym,
                res.getpairstatescount.same_asym,
                res.getpairstatescount.fuz_ident,
                res.getpairstatescount.fuz_sym,
                res.getpairstatescount.fuz_asym,
                res.getpairstatescount.unique)


    # return array of tuples
    # tuple = (first_event_id, type, prefixes, unmatched_prefixes, hast_distance, parent, child, executions)
    #         (           int,  str,      int,                int,           int,    str,   str,        int)
    def get_pairs(self, host: int,
                     intypes: list):

        req = pb.Request()
        req.command = pb.GETPAIRS
        req.getpairs.host = host
        for thisone in intypes:
            item = req.getpairs.type.append(thisone)

        res = self._send_and_check(req, pb.GETPAIRS)
        result = []
        for item in res.getpairs.entry:
            result.append( (item.eventid,
                            item.type,
                            item.total_prefixes,
                            item.unique_prefixes,
                            item.hash_dist,
                            item.parent,
                            item.child,
                            item.execs) )

        print('API: get_pairs: got:', len(result))
        return result
