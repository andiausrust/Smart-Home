from configparser import ConfigParser
from shutil import get_terminal_size
from os import environ
from sys import exit, version, stdout

try:
    import pandas as pd
except ImportError:
    print("ModuleNotFoundError: No module named 'pandas'")
    print("")
    print('Is this the correct Python execution environment?')
    exit(1)

import re
from pathlib import Path

# possible execution environment
SHELL    = 0
IPYTHON  = 1
NOTEBOOK = 2


class Config:
    DATABASES_CONFIG = "db.ini"

    def __init__(self):
        pass

    @staticmethod
    def get_database(dbstring: str):
        tempurl = dbstring

        # is passed string a URL?
        match = re.match(r"postgresql\+psycopg2:", tempurl)

        if not match:
            # try default .ini
            filename = Path(Config.DATABASES_CONFIG)
            if filename.is_file():
                # parse .ini
                cp = ConfigParser()
                cp.read(filename)
                if not cp.has_section("Databases"):
                    print("help! There is no 'Databases' section in", "'"+str(filename)+"'")
                    quit()
                di = dict(cp.items("Databases"))
                # and look for requested alias
                if dbstring not in di:
                    print("Help! This is an unknown db alias:")
                    print(dbstring)
                    print(di)
                    exit(1)
                else:
                    tempurl = di[dbstring]

            else:
                print("Passed db specifications is neither URL or a known db alias? --- " +
                      Config.DATABASES_CONFIG+" not found!")
                print(dbstring)
                exit(1)

#        print("accessing "+tempurl)
        return tempurl


    @staticmethod
    def get_python_version() -> str:
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

        return "Python "+version.replace('\n', '')+" ("+environment+")"


    @staticmethod
    def detect_environment():
        """ Try to autodetect runtime environment """
        try:
            __IPYTHON__     # <=== red in PyCharm IDE is here ok!
        except NameError:
#            print("In shell")
            return SHELL
        else:
            from IPython import get_ipython
            from IPython.terminal.interactiveshell import TerminalInteractiveShell

            if type(get_ipython()) == TerminalInteractiveShell:
#                print("In IPython")
                return IPYTHON
            else:
#                print("In Notebook")     # a notebook is IPython.kernel.zmq.zmqshell.ZMQInteractiveShell
                return NOTEBOOK


    @staticmethod
    def _set_console_sizes():
        if stdout.isatty():
            terminal = get_terminal_size()
    #        if terminal.columns == 0:   # pipe to file
            col = int((terminal.columns-5)/10*6)
            width = terminal.columns-5
        else:
            col = int(215/10*6)
            width = 210
#        print(col, width)
        pd.set_option('max_rows',      100)
        pd.set_option('max_colwidth',  col)
        pd.set_option('display.width', width)


    @staticmethod
    def set_terminal_size():
        """ Set Pandas terminal output options depending on current runtime environment """

        env = Config.detect_environment()

        if env == SHELL:
            Config._set_console_sizes()

        elif env == IPYTHON:
            Config._set_console_sizes()

        elif env == NOTEBOOK:
                pd.set_option('max_rows',      100)
                pd.set_option('max_colwidth',  int(215/10*6))
                pd.set_option('display.width', 210)   # your browser is probably different, but there is no way to autodetect this better?

        else:
            print("Help! unknown environment")
            exit(1)
