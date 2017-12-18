import sys
from util.config import Config, SHELL, IPYTHON, NOTEBOOK

from importlib import import_module

from r4.cmdtemplate import CommandTemplate
#            print name   import module name
VERSION = [("IPython",    "IPython"),
           ("Numpy",      "numpy"),
           ("Pandas",     "pandas"),
           ("SQLAlchemy", "sqlalchemy"),
           ("psycopg2",   "psycopg2"),
           ("matplotlib", "matplotlib"),
           ("bokeh",      "bokeh"),
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
        environment = Config.detect_environment()
        if environment == SHELL:
            environment = "shell"
        elif environment == IPYTHON:
            import IPython
            environment = "IPython "+IPython.__version__+", shell"
        elif environment == NOTEBOOK:
            import IPython
            environment = "IPython "+IPython.__version__+", notebook"
        else:
            environment = "unknown!"

        print("running on:")
        print("     Python", sys.version.replace('\n', ''), "("+environment+")")

        print("\nruntime environment:")
        for i in VERSION:
            try:
                module = import_module(i[1])
                version = module.__version__
            except ImportError:
                version = "...not installed!"
            print("{0:>11} {1:}".format(i[0], version))


    def run(self, **kwargs):
        CmdVersion.print_versions()
