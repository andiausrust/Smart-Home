from sys import exit
import re
import pandas as pd
import datetime as dt

class ModelTemplate:
    ''' Minimal set of functions every model implements '''

    def get_modelname(self):
        print("error: model has no get_name implementation")
        exit(1)

    def __init__(self, **kwargs):    # traces,
        print("error: model has no __init__ implementation")
        exit(1)

    def consume_event(self, ev: dict):
        """ Consume one event row from database """
        print("error: model has no consume_event implementation")
        exit(1)


    # def get_state(self, timetick: dt.datetime):
    #     """ Compute snapshot of current state of model """
    #     print("error: model has no get_state implementation")
    #     pass
    #
    # def save_state(self, timetick: dt.datetime):
    #     """ Compute snapshot of current state and save as this timetick """
    #     print("error: model has no save_result implementation")
    #     pass
    #
    #
    # def print_result(self, result=None):
    #     """ Print a specific result from model """
    #     print("error: model has no print_result implementation")
    #     pass

    def result_df(self, regex=None) -> pd.DataFrame:
        """ Return columns in 'result' dict as selected by 'regex' as DataFrame """
        if regex:
            # get one random item from dict, and get keys from this random (dict) item
            # FIXME: how to do this better? - this is not efficient...
            keys = self.result[next(iter(self.result))].keys()

            if type(regex) == str:
                comp_regexe = re.compile(regex)
                columns = list(filter(comp_regexe.search, keys))
            else:
                columns = list(filter(regex.search, keys))

            df = pd.DataFrame.from_dict(self.result, orient='index')
            return df[columns]
        else:
            return pd.DataFrame.from_dict(self.result, orient='index')


    @staticmethod
    def to_df(thisdict, name=None, index=None) -> pd.DataFrame:
        """ convert dict to DataFrame with name 'name' and set index column from 'index' """
        df = pd.DataFrame.from_dict(thisdict, orient='index')
        if index:
            df = df.set_index(index)
        if name:
            df.index.name=name

        if df.size>0:
            df.sort(inplace=True, ascending=False)
        return df
