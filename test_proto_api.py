#!/usr/bin/env python3
from pprint import pprint
from time import sleep

import pika

from util.config import Config
from protoapi.moduleapi2 import ModuleApi2
from protoapi.protoclient import Protoclient
from protoapi.protoserver import Protoserver
from protoapi.rabbitmq import Rabbitmq


#indb1 = 'ng4'; inrange1 = [8, 3997625, 8606957]
#indb2 = 'ng4'; inrange2 = [9, 3997624, 8606957]
db1 = Config.get_database('ng4')
db2 = Config.get_database('ng4')

mod = None
rmq = None
server = Protoserver()


# # OPTION 1: pure local calls
# mod = ModuleApi2()


# OPTION 2: via protobuf en-/decoding
# def s_and_r(req: bytes) -> bytes:  # NOP send and receive
#     res = server.parse_and_execute(req)
#     print("s&r:", len(req), "->", len(res) )
#     return res
#
# # via Protobuf
# mod = Protoclient(s_and_r)
# print(mod.getversion(0))


# OPTION 3: protobuf over RabbitMQ
url = 'amqp://server:5672'
rmq = Rabbitmq(url, Rabbitmq.REQUEST_Q,
                    Rabbitmq.RESPONSE_Q)


def rmq_s_and_r(req: bytes) -> bytes:
    rmq.publish(Rabbitmq.REQUEST_Q, req)
    res = rmq.receive(Rabbitmq.RESPONSE_Q)
    # print("s&r:", len(req), "->", len(res) )
    return res


mod = Protoclient(rmq_s_and_r)
print(mod.getversion(0))


mod.connect("cmp4b", db1, 5, db2, 6)

#mod.consume(1069, 8606957,
#            1069, 8606957)

mod.consume(1069, 306957,
            1069, 306957)

#mod.connect("", db1, 8, db2, 9)
#mod.consume(3997625, 8606957,
#            3997624, 8606957)
#
#mod.consume(3997625, 4100000,
#            3997624, 4100000)
#mod.consume(4100001, 4500000,
#            4100001, 4500000)

mod.run_evaluation(1)
mod.run_evaluation(2)

print("\n---------------------------------\n")

print(mod.get_pair_states_count(1))
pprint(mod.get_pairs(1, [ModuleApi2.SAME_ASYM, ModuleApi2.FUZ_ASYM, ModuleApi2.UNIQUE]) )

print("\n---------------------------------\n")

print(mod.get_pair_states_count(2))
pprint(mod.get_pairs(2, [ModuleApi2.SAME_ASYM, ModuleApi2.FUZ_ASYM, ModuleApi2.UNIQUE]) )

print("\n---------------------------------\n")

print("\n----done---\n")


mod.reinit()
if rmq:
    rmq.close()
