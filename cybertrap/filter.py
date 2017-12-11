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

    @staticmethod
    def remove_harddiskvolume(binary_path):
            match = re.match(r"\\Device\\HarddiskVolume(\d*)", binary_path, re.IGNORECASE)
            if match:
                return match.string[match.end(0):]
            else:
                # src_file_name ILIKE '\\device\\mup%'
                match = re.match(r"\\Device\\mup", binary_path, re.IGNORECASE)
                if match:
                    return 'NO'
                else:
                    return binary_path


    @staticmethod
    def run_filters(ev):
        ev[PROCESS_NAME] = Filter.remove_harddiskvolume(ev[PROCESS_NAME])

        if ev[PARENT_PROCESS_NAME] is not None:
            ev[PARENT_PROCESS_NAME] = Filter.remove_harddiskvolume(ev[PARENT_PROCESS_NAME])

        if ev[TYPE_ID] == FILE:
            ev[SRC_FILE_NAME] = Filter.remove_harddiskvolume(ev[SRC_FILE_NAME])

            if ev[TYPE] == RENAME:
                ev[DST_FILE_NAME] = Filter.remove_harddiskvolume(ev[DST_FILE_NAME])
