import sys
from util.config import Config

from importlib import import_module

from r4.cmdtemplate import CommandTemplate
#            print name   import module name
VERSION = [("IPython",    "IPython"),
           ("Numpy",      "numpy"),
           ("Pandas",     "pandas"),
           ("SQLAlchemy", "sqlalchemy"),
           ("psycopg2",   "psycopg2"),
           ("nilsimsa",   "nilsimsa"),
           ("matplotlib", "matplotlib"),
           ("bokeh",      "bokeh"),
           ("pika",       "pika"),
           ("protobuf",   "google.protobuf"),
           ("flask",      "flask"),
           ("jinja2",     "jinja2"),
           ]


class CmdVersion(CommandTemplate):
    NAME = 'version'
    HELP = 'show runtime library versions'

    @staticmethod
    def add_subparser(subparsers):
        parser = subparsers.add_parser(CmdVersion.NAME,
                 aliases=['ver'],
                 help=CmdVersion.HELP)
        parser.set_defaults(cls=CmdVersion)


    @staticmethod
    def print_versions():

        print("running on:")
        print(Config.get_python_version())

        print("\nruntime environment:")
        for i in VERSION:
            try:
                module = import_module(i[1])
                if i[1]!= 'nilsimsa':
                    version = module.__version__
                else:
                    version = "available"
            except ImportError:
                version = "...not installed?"
            print("{0:>11} {1:}".format(i[0], version))


    def run(self, **kwargs):
        CmdVersion.print_versions()
