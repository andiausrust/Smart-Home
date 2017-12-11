# escape sequences generators for a prettier output on terminal


class RawTerm:

    @staticmethod
    def setfg(col: int):
        """ set text foreground color (0-255) """
        return '\x1b[38;5;'+str(col)+'m'

    @staticmethod
    def resetfg():
        """reset text foreground color to terminal default"""
        return '\x1b[39m'


    @staticmethod
    def bold():
        return '\x1b[01m'

    @staticmethod
    def not_bold():
        return '\x1b[22m'


    @staticmethod
    def normal():
        return '\x1b[0m'


    @staticmethod
    def gotox(col: int):
        """ jump cursor to column x """
        return '\x1b['+str(col)+'G'
