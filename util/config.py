from configparser import ConfigParser
from os import get_terminal_size
from sys import exit

import pandas as pd

# possible execution environment
SHELL    = 0
IPYTHON  = 1
NOTEBOOK = 2


class Config:
    DATABASES_CONFIG = "db.ini"

    def __init__(self, filename=DATABASES_CONFIG):
        self.cp = ConfigParser()
        self.cp.read(filename)
        self.filename = filename

    def databases(self) -> dict:
        if not self.cp.has_section("Databases"):
            print("help! There is no 'Databases' section in", "'"+self.filename+"'")
            quit()
        return dict(self.cp.items("Databases"))



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
        terminal = get_terminal_size()
#        if terminal.columns == 0:   # pipe to file
        col = int((terminal.columns-5)/10*6)
        width = terminal.columns-5
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
