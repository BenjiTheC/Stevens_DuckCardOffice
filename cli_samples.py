""" Use only python script to complete the needed functionality"""

import os
import sqlite3
from datetime import datetime
from stevens_systems import Slate, Blackboard, JSA
from nerdy_ben import NerdyBen

TODAY = datetime.now().strftime('%y%m%d')
DUCKCARD = os.path.join(os.pardir, 'DuckCard_data')
WRITE_TO = os.path.join(DUCKCARD, 'NerdyBen')
SLATE = os.path.join(DUCKCARD, 'Slate')
BLACKBOARD = os.path.join(DUCKCARD, 'Blackboard')
JSA_ = os.path.join(DUCKCARD, 'JSA')

DATABASE = os.path.join(os.curdir, 'duckcard.db')


def main():
    """ ENTRANCE"""
    sla = Slate(SLATE, DATABASE)
    bb = Blackboard(BLACKBOARD, DATABASE)
    jsa = JSA(JSA_, DATABASE)
    benji = NerdyBen(DATABASE, WRITE_TO)

    first_time = True
    bb.insert_data(first_time=first_time, date=TODAY)

    # TODO:
    #   init: first time -> print info and build + insert data
    #   update: date=TODAY, insert data
    #   get-silly: error distinguish
    #   get-import: to_import
    #   get-print: to_print
    #   get-remind: TODO: functionality under develop
    #   check-import: imported_check
    