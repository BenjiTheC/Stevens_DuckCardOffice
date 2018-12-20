""" Simulate Slate, Blackboard, JSA, and TheBenji XD"""

import os
import re
#import sys
import sqlite3
from datetime import datetime
from tabulate import tabulate
from QueryLib import Query
from read_file import file_reading_gen


def find_date(dir_path, date=None):
    """ find the file with the specific date in given dir"""
    if not os.path.isdir(dir_path):
        raise OSError(f'{dir_path} is not a valid directory!')

    for path in os.listdir(dir_path):
        if os.path.isfile(os.path.join(dir_path, path)) and date in path:
            return os.path.join(dir_path, path)
    # iteration over without return
    raise FileNotFoundError('There is no file received today!')

def to_upper(s: str):
    """ Return the upper case version of the first part of given string splited by white space"""
    return s.strip().split(' ')[0].upper()

def get_status(status_string: str):  # TODO: the new status 'printed' to be added
    """return the status from the long string"""
    status_tup = ('approved', 'pending', 'rejected')
    for status in status_tup:
        if status in status_string:
            return status

class System:
    """ Super class for Slate, Blackboard, JSA.
        define the __init__ and other potential shared attr/methods
    """

    def __init__(self, source_dir=None, database=None):
        """ define the connection path of database, dir path for updating database"""
        self._source_dir = source_dir
        self._database = database
    
    def create_table(self):
        """ Create table with proper query"""

    def insert_one_file(self, file_path=None, db_connect=None, date=None):
        """ Insert one specific file into table"""

    def insert_data(self, first_time=False, date=None, pattern=r''):
        """ insert data into a table
            if first_time:
                dump all of the data into the database
            if date:
                assumed that there are records in it: need a if statement to check
                only import the specific date.

            first_time and date can not be True at the same time
        """

    def print_count(self):
        """ Print the counting result group by received_date"""

class Slate(System):
    """ Slate is responsible for generating new Stevens identifications for newly admitted students
        of Steven. There are two general types of students, brand new students and continuing students.
        However there are some continuing students forget to imply that they are former students of
        Stevens and Slate generate a set of new Stevens ID for them.
    """

    def __init__(self, source_dir=None, database=None):
        super().__init__(source_dir, database)
        self.create_table()
        
    def create_table(self):
        """ create table Slate in database"""
        connection = sqlite3.connect(self._database)
        connection.execute(Query.create_slate)
        connection.commit()
        connection.close()

    def insert_one_file(self, file_path=None, db_connect=None, date=None):
        """ Insert one specific file into table"""
        if not db_connect:
            raise ConnectionError('No connection of database provided!')
        
        cursor = db_connect.cursor()

        for cwid, first, middle, last, username, email, dcisionfn, prnd, defer, dcisionln, pchange, special \
        in file_reading_gen(file_path, 12, header=True):
            data = (cwid, to_upper(first), to_upper(middle), to_upper(last), first, middle, last, email, username, date if date else 'undated')
            cursor.execute(Query.insert_slate, data)
            db_connect.commit()
    
    def insert_data(self, first_time=False, date=None, pattern=r'Export_([\d]{6}).*\.csv'):
        """ insert data into table Blackboard"""
        if first_time and date:
            raise ValueError("You either insert data in a specific date or dump all, can't do both!")

        connection = sqlite3.connect(self._database)

        if first_time:
            for slate_file in os.listdir(self._source_dir):
                reg = re.search(pattern, slate_file) # extract the date
                if reg:
                    path = os.path.join(self._source_dir, slate_file)
                    self.insert_one_file(path, connection, reg.group(1))

        if date:
            path = find_date(self._source_dir, date)
            self.insert_one_file(path, connection, date)
            
        connection.close()   

    def print_count(self):
        """ Print the count group by date"""
        connection = sqlite3.connect(self._database)
        cursor = connection.cursor()

        pp_lst = list()
        for row in cursor.execute(Query.count_by_date_slate):
            pp_lst.append(row)

        print('\nSlate information:')
        print(tabulate(pp_lst, headers=['received_date', 'count'], showindex='always', tablefmt='fancy_grid'))
        
        connection.close()

class Blackboard(System):
    """ Blackboard is responsible for providing the data of people who have unified Stevens identification.
        It's used to build the reference for comparsion of the newly admitted students.
    """

    def __init__(self, source_dir=None, database=None):
        super().__init__(source_dir, database)
        self.create_table()
        
    def create_table(self):
        """ create table Blackboard in database"""
        connection = sqlite3.connect(self._database)
        connection.execute(Query.create_bb)
        connection.commit()
        connection.close()

    def insert_one_file(self, file_path=None, db_connect=None, date=None):
        """ Insert one specific file into table"""
        if not db_connect:
            raise ConnectionError('No connection of database provided!')
        
        cursor = db_connect.cursor()
        in_db = list()

        for cwid, in cursor.execute(Query.get_indb_bb):
            in_db.append(cwid)

        for cwid, first, middle, last, uggr, exp in file_reading_gen(file_path, 6, header=True):
            if cwid in in_db:
                continue
            data = (cwid, to_upper(first), to_upper(middle), to_upper(last), first, middle, last, date)
            cursor.execute(Query.insert_bb, data)
        cursor.execute(Query.update_bb)  # clean up the null value
        db_connect.commit()

    def insert_data(self, first_time=False, date=None, pattern=r'InCampusPersonnel_([\d]{6})\.csv'):
        """ Inherit and override the super class's method"""
        if first_time and date:
            raise TypeError("You can't do first_time and date at the same time!")

        connection = sqlite3.connect(self._database)

        if first_time:
            date_lst = list()
            for bb_file in os.listdir(self._source_dir):
                reg = re.search(pattern, bb_file)
                if reg:
                    date_lst.append(datetime.strptime(reg.group(1), '%y%m%d'))

            while date_lst:
                date = date_lst.pop(date_lst.index(min(date_lst))).strftime('%y%m%d')  # pop the earliest date file
                path = find_date(self._source_dir, date)
                self.insert_one_file(path, connection, date)
                date = None

        if date:
            path = find_date(self._source_dir, date)
            self.insert_one_file(path, connection, date)

        connection.close()

    def print_count(self):
        """ Print the count group by date"""
        connection = sqlite3.connect(self._database)
        cursor = connection.cursor()

        pp_lst = list()
        for row in cursor.execute(Query.count_by_date_bb):
            pp_lst.append(row)

        print('\nBlackboard information')
        print(tabulate(pp_lst, headers=['received_date', 'count'], showindex='always', tablefmt='fancy_grid'))
        
        connection.close()
    
class JSA(System):
    """ JSA is responsible for managing the photo upload for newly admitted students in 
        Stevens, and you will recevied an everyday .csv file contained all of the records
        of uploading attempts and the current status of photos that were uploaded.
        One individual can have multiple records if he/she uploads more than one time.
    """

    def __init__(self, source_dir=None, database=None):
        super().__init__(source_dir, database)
        self.create_table()

    def create_table(self):
        """ create table JSA in database"""
        connection = sqlite3.connect(self._database)
        connection.execute(Query.create_jsa)
        connection.commit()
        connection.close()

    def insert_one_file(self, file_path=None, db_connect=None, date=None):
        """ It's more complicated than Bb and Slate because it's involved with updating the data"""
        cursor = db_connect.cursor()

        for cwid, first, last, status, submitdate, email, uggr in file_reading_gen(file_path, 7):
            
            # record = [cwid, first, last, status, submit_date, received_date]
            record = cursor.execute(Query.select_existed_jsa, (cwid, )).fetchone()
            status = get_status(status)

            # new record
            if not record:    
                data = (cwid, first, last, status, submitdate, date)
                cursor.execute(Query.insert_jsa, data)

            # existed record but has a status change
            # format of submitDate: mm/dd/yy hh:mm:ss --> %m/%d/%y %H:%M:%S
            elif record and status != record[3] \
                and datetime.strptime(record[4], '%Y-%m-%d %H:%M:%S') <= datetime.strptime(submitdate, '%Y-%m-%d %H:%M:%S'): 
                data = (status, submitdate, date, cwid)
                cursor.execute(Query.update_jsa, data)

            elif record and status == record[3]:
                pass  # for future potential use

            db_connect.commit()

        
        db_connect.commit()

    def insert_data(self, first_time=False, date=None, pattern=r'received_jsa_([\d]{6})\.csv'):
        """ Inherit and override the super class's method"""
        if first_time and date:
            raise TypeError("You can't do first_time and date at the same time!")

        connection = sqlite3.connect(self._database)

        if first_time:
            date_lst = list()
            for jsa_file in os.listdir(self._source_dir):
                reg = re.search(pattern, jsa_file)
                if reg:
                    date_lst.append(datetime.strptime(reg.group(1), '%y%m%d'))

            while date_lst:
                date = date_lst.pop(date_lst.index(min(date_lst))).strftime('%y%m%d')  # pop the earliest date file
                path = find_date(self._source_dir, date)
                self.insert_one_file(path, connection, date)
                date = None

        if date:
            path = find_date(self._source_dir, date)
            self.insert_one_file(path, connection, date)

        connection.close()

    def print_count(self):
        """ print the count group by date"""
        connection = sqlite3.connect(self._database)
        cursor = connection.cursor()

        pp_lst = list()
        for row in cursor.execute(Query.count_by_date_jsa):
            pp_lst.append(row)

        print('\nJSA information')
        print(tabulate(pp_lst, headers=['received_date', 'count'], showindex='always', tablefmt='fancy_grid'))
        
        connection.close()       
        
def main():
    """ for test"""
    db = os.path.join(os.curdir, 'duckcard.db')  #os.path.join(DUCKCARD, 'duckcard.db')

    TODAY = datetime.today().strftime('%y%m%d')
    DUCKCARD = os.path.join(os.pardir, 'DuckCard_data')
    SLATE = os.path.join(DUCKCARD, 'Slate')
    BLACKBOARD = os.path.join(DUCKCARD, 'Blackboard')
    JSA_ = os.path.join(DUCKCARD, 'JSA')

    sla = Slate(SLATE, db)
    #sla.insert_data(first_time=True)  # date=TODAY

    bb = Blackboard(BLACKBOARD, db)
    #bb.insert_data(date=TODAY)  # date=TODAY first_time=True

    jsa = JSA(JSA_, db)
    #jsa.insert_data(first_time=True)  # date=TODAY

    #bb.print_count()
    sla.print_count()
    #jsa.print_count()


if __name__ == '__main__':
    main()
