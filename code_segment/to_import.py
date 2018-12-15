""" generate the file for to be imported students."""

import os
from datetime import datetime
from read_file import file_reading_gen

# static var, path to data dir
DUCKCARD_DATA = os.path.join(os.path.abspath(os.path.pardir), 'DuckCard_data')
TO_IMPORT = os.path.join('errorDistinguish', 'toImport')
BRN = os.path.join('errorDistinguish', 'brn')
CONF = os.path.join('errorDistinguish', 'sus')
RAW_EXPORT = os.path.join('errorDistinguish', 'rawExport')

class Combine:
    """ Go to BRN and CONF, find the files on specific day and combine them with the give time span

    """
    
    def __init__(self, brn=os.path.join(DUCKCARD_DATA, BRN), 
                        conf=os.path.join(DUCKCARD_DATA, CONF), 
                        to_import=os.path.join(DUCKCARD_DATA, TO_IMPORT),
                        raw_exprot=os.path.join(DUCKCARD_DATA, RAW_EXPORT)):
        self.brn = brn
        self.conf = conf
        self.to_import = to_import
        self.raw_export = raw_exprot
