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
