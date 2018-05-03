#!/usr/bin/env python3
from pprint import pprint
from util.config import Config
from protoapi.moduleapi2 import ModuleApi2


#indb1 = 'ng4'; inrange1 = [8, 3997625, 8606957]
#indb2 = 'ng4'; inrange2 = [9, 3997624, 8606957]
db1 = Config.get_database('ng4')
db2 = Config.get_database('ng4')


# get net instance
mod = ModuleApi2()

# setup database connection
mod.connect("", db1, 5, db2, 6)

mod.consume(1069, 8606957,
            1069, 8606957)

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
pprint(mod.get_pairs(1, [ModuleApi2.SAME_ASYM, ModuleApi2.FUZ_ASYM, ModuleApi2.UNIQUE]))

print("\n---------------------------------\n")

print(mod.get_pair_states_count(2))
pprint(mod.get_pairs(2, [ModuleApi2.SAME_ASYM, ModuleApi2.FUZ_ASYM, ModuleApi2.UNIQUE]))
