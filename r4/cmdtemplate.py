class CommandTemplate:
    NAME = 'fill me'
    HELP = 'fill me'

    @staticmethod
    def add_subparser(subparsers):
        print("error: cannot add subparser for empty command")
        quit()


    def run(self, args):
        print("error: command has not body to execute")
        quit()

    def print_result(self, result=None):
        print("error: command has print_result implementation")
        quit()
