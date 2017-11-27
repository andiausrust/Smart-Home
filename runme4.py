#!/usr/bin/env python3

# uncomment for debugging to see if correct LOCALE is set (when called in Docker container)
#import locale; import sys;
#print(locale.getpreferredencoding())
#print(sys.getdefaultencoding())
#print(sys.stdout.encoding)
#sys.exit(1)

from sys import argv

# special case for 'version' command so fewer lib imports are needed
from r4.cmd_version import CmdVersion
if len(argv)>1:
    if argv[1]=="version":
        CmdVersion.print_versions()
        exit(0)

print("not implemented, yet")

exit(1)


#from r3.cmd_pgrun3 import CmdPgRun3
#from r3.cmd_pgrun3d import CmdPgRun3d
#from r3.cmd_pgstat import CmdPgStat

#def add_r3_commands(subparsers):
#    CmdVersion.add_subparser(subparsers)
#    CmdPgStat.add_subparser(subparsers)
#    CmdPgRun3.add_subparser(subparsers)
#    CmdPgRun3d.add_subparser(subparsers)



import argparse
from sys import exit

from util.config import Config


Config.set_terminal_size()

parser = argparse.ArgumentParser(add_help=True)
subparsers = parser.add_subparsers(help='commands')
#add_r3_commands(subparsers)

args = parser.parse_args()
dictargs = vars(args)

if "cls" not in dictargs:
    print('usage: runme4.py command [args]')
    exit(1)

command = args.cls()
command.run(**dictargs)
