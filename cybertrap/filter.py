# Filter and workaround for various oddities in Cybertrap data stream

# this is getting shorter and shorter! :-)

import re
from pprint import pprint
from cybertrap.dbconst import *


class Filter:

##############################################################################

    # @staticmethod
    # def filter_bin_path(bin_path):
    #     bin_path =  Filter.remove_harddiskvolume(bin_path)
    #     # return bin_path.strip()
    #     return bin_path
    #
    # @staticmethod
    # def filter_src_file(src_file):
    #     src_file = Filter.remove_harddiskvolume(src_file)
    #     # return src_file.strip()
    #     return src_file
    #
    #
    # @staticmethod
    # def filter_dst_file(dst_file):
    #     dst_file = Filter.remove_harddiskvolume(dst_file)
    #     # return dst_file.strip()
    #     return dst_file

##############################################################################
    DUMMY_EVENT = r'Dummy Process Event'

    @staticmethod
    def remove_leading_binary_name(cmdline_path:str) -> str:
        if cmdline_path == Filter.DUMMY_EVENT:
            return cmdline_path

        else:
            index = cmdline_path.find(' ')
            if index == -1:
                return ""
            else:
                if cmdline_path[0] == '"':
                    index2 = cmdline_path.find('"', 1)
                    if index2 == -1:
                        print("help! I can't find closing \" in ", cmdline_path)
                        quit()
                    else:
                        return cmdline_path[index2+1:]
                else:
                    return cmdline_path[index+1:]

    @staticmethod
    def remove_harddiskvolume(binary_path:str) -> str:
            match = re.match(r"\\Device\\HarddiskVolume(\d*)", binary_path, re.IGNORECASE)
            if match:
                found = match.string[match.end(0):]
                if len(found)==0:
                    return r'\__EMPTY_ACCESS'
                else:
                    return found
            else:
                # src_file_name ILIKE '\\device\\mup%'
                match = re.match(r"\\Device\\mup", binary_path, re.IGNORECASE)
                if match:
                    return r'\__UNHANDLED'+binary_path
                else:
                    return binary_path


    @staticmethod
    def run_filters(ev):
        ev[PROCESS_NAME] = Filter.remove_harddiskvolume(ev[PROCESS_NAME])

        if ev[PROCESS_NAME] == SYSTEM_PROCESS_NAME:
           ev[PROCESS_NAME] = r"\SYSTEM"
        elif ev[PROCESS_NAME] == DUMMY_PROCESS_NAME:
             ev[PROCESS_NAME] = r"\DUMMY_PROCESS_EVENT"

        if ev[PARENT_PROCESS_NAME] is not None:
            ev[PARENT_PROCESS_NAME] = Filter.remove_harddiskvolume(ev[PARENT_PROCESS_NAME])

            if ev[PARENT_PROCESS_NAME] == SYSTEM_PROCESS_NAME:
               ev[PARENT_PROCESS_NAME] = r"\SYSTEM"
            elif ev[PARENT_PROCESS_NAME] == DUMMY_PROCESS_NAME:
                 ev[PARENT_PROCESS_NAME] = r"\DUMMY_PROCESS_EVENT"

        if ev[GRANDPARENT_PROCESS_NAME] is not None:
            ev[GRANDPARENT_PROCESS_NAME] = Filter.remove_harddiskvolume(ev[GRANDPARENT_PROCESS_NAME])

            if ev[GRANDPARENT_PROCESS_NAME] == SYSTEM_PROCESS_NAME:
               ev[GRANDPARENT_PROCESS_NAME] = r"\SYSTEM"
            elif ev[GRANDPARENT_PROCESS_NAME] == DUMMY_PROCESS_NAME:
                 ev[GRANDPARENT_PROCESS_NAME] = r"\DUMMY_PROCESS_EVENT"

        if ev[TYPE_ID] == PROCESS:
            if ev[WORKING_DIRECTORY] is not None:
                ev[WORKING_DIRECTORY] = Filter.remove_harddiskvolume(ev[WORKING_DIRECTORY])

        if ev[TYPE_ID] == FILE:
            ev[SRC_FILE_NAME] = Filter.remove_harddiskvolume(ev[SRC_FILE_NAME])

            if ev[TYPE] == RENAME:
                ev[DST_FILE_NAME] = Filter.remove_harddiskvolume(ev[DST_FILE_NAME])
