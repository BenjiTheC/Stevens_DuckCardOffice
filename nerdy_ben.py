""" All the data select operations in a class."""

import os
import sqlite3
from datetime import datetime
from read_file import file_reading_gen
from QueryLib import Query

TODAY = datetime.now().strftime('%y%m%d')
DUCKCARD = os.path.join(os.pardir, 'DuckCard_data')
DATABASE = os.path.join(os.curdir, 'duckcard.db')
WRITE_TO = os.path.join(DUCKCARD, 'NerdyBen')

""" The folders under directory 'NerdyBen' is consistent:
    - brn
    - con
    - sus
    - conf
    - toPrint
    - toImport
    - toRemind
"""

def get_one_column(file_path, fields, col, sep=',', header=True):
    """ Only get one specific column in a .csv file, col starts from 0.""" 
    if fields <= col:
        raise IndexError(f'The file {file_path} only has {fields} fields but you are asking for {col + 1}th column!')

    res = list()
    for row in file_reading_gen(file_path, fields, sep, header):
        res.append(row[col])

    return res

class NerdyBen:
    """ This class contains all the data analysis process needed for the DuckCard office's newly
        incomming students' duckcard printing process
    """

    brn = 'brn'
    con = 'con'
    sus = 'sus'
    conf = 'conf'
    to_import_ = 'toImport'
    to_print_ = 'toPrint'
    to_remind_ = 'toRemind'

    def __init__(self, database=None, writeto_dir=None):
        self._database = database
        self._writeto_dir = writeto_dir

    def error_prone_distinguish(self, date=None):
        """ Cross check the data from Slate and Blackboard, find error proned students(sus), new
            students(brn) and normal continuing students(con)
        """
        path_con = os.path.join(self._writeto_dir, NerdyBen.con, f'con_{date}.csv')
        path_sus = os.path.join(self._writeto_dir, NerdyBen.sus, f'sus_{date}.csv')
        path_brn = os.path.join(self._writeto_dir, NerdyBen.brn, f'brn_{date}.csv')

        connection = sqlite3.connect(self._database)
        cursor = connection.cursor()

        # find continuing students
        if cursor.execute(Query.find_con, (date, )).fetchall():
            with open(path_con, 'w') as fwrite:
                fwrite.write('CWID,first,middle,last\n')
                for cwid, first, middle, last in cursor.execute(Query.find_con, (date, )):
                    fwrite.write(f'{cwid},{first},{middle},{last}\n')
        
        # find suspect students
        if cursor.execute(Query.find_sus, (date, )).fetchall():
            with open(path_sus, 'w') as fwrite:
                fwrite.write('CWID,first,middle,last\n')
                for cwid, first, middle, last in cursor.execute(Query.find_sus, (date, )):
                    fwrite.write(f'{cwid},{first},{middle},{last}\n')

        # find brand new students
        with open(path_brn, 'w') as fwrite:
            fwrite.write('CWID,first,middle,last\n')
            for cwid, first, middle, last in cursor.execute(Query.find_brn, (date, ) * 3):
                fwrite.write(f'{cwid},{first},{middle},{last}\n')

        connection.close()

    def to_import(self, date=None, uggr='GR', exit_date='12/31/22'):
        """ After Ms. Edge finishes checking the sus students, combine the new students in conf 
            and brn to send to Kristen.
        """
        path_brn = os.path.join(self._writeto_dir, NerdyBen.brn, f'brn_{date}.csv')
        path_conf = os.path.join(self._writeto_dir, NerdyBen.conf, f'conf_{date}.csv')
        path_toimport = os.path.join(self._writeto_dir, NerdyBen.to_import_, f'to_import_{date}.csv')
        status = {'YES': True, 'NO': False}

        with open(path_toimport, 'w') as fwrite:
            fwrite.write('CWID,first,middle,last,UG/GR,ExitDate\n')

            for cwid, first, middle, last in file_reading_gen(path_brn, 4, header=True):
                fwrite.write(f'{cwid},{first},{middle},{last},{uggr},{exit_date}\n')

            for cwid, first, middle, last, is19s in file_reading_gen(path_conf, 5, header=True):
                if status[is19s.upper()]:
                    fwrite.write(f'{cwid},{first},{middle},{last},{uggr},{exit_date}\n')    

    def doublecheck_imported(self, date=None):
        """ Check if Kristen has imported all students in the .csv file sent to her."""
        path_toimport = os.path.join(self._writeto_dir, NerdyBen.to_import_, f'to_import_{date}.csv')
        cwid_in_bb = list()

        connection = sqlite3.connect(self._database)
        cursor = connection.cursor()

        for cwid, in cursor.execute(Query.cwid_in_bb):
            cwid_in_bb.append(cwid)

        connection.close()

        not_in = 0
        to_import = get_one_column(path_toimport, 6, 0)
        for cwid in to_import:
            if cwid not in cwid_in_bb:
                print(f"{cwid} hasn't been imported yet.")
                not_in += 1
        print(f'Have checked {len(to_import)} CWIDs, {not_in} are not imported yet.' \
                if not_in else f'All CWIDs are imported.')
            
    def to_print(self, date=None, status='approved'):
        """ Extract from JSA database for those whose photos have been uploaded and approved but their
            cards are not printed yet.
        """
        path_toprint = os.path.join(self._writeto_dir, NerdyBen.to_print_, f'to_print_{date}.csv')
        connection = sqlite3.connect(self._database)
        cursor = connection.cursor()

        if cursor.execute(Query.select_status_jsa, (date, status)).fetchall():
            with open(path_toprint, 'w') as fwrite:
                fwrite.write('CWID,fisr,last,received_date\n')

                for cwid, first, last, received_date in cursor.execute(Query.select_status_jsa, (date, status)):
                    fwrite.write(f'{cwid},{first},{last},{received_date}\n')

        connection.close()

    def to_remind(self, date=None):
        """ Extract from JSA database for those who have been imported into the Blackboard but have not
            uploaded their photos yet.
        """

def main():
    """ Test"""
    benji = NerdyBen(DATABASE, WRITE_TO)
    #benji.error_prone_distinguish(date='181217')
    #benji.to_import(date='181108')
    #benji.doublecheck_imported(date='181108')
    #benji.to_print(date='181210')

if __name__ == '__main__':
    main()
