""" Simulate Slate, Blackboard, JSA, and TheBenji XD"""

import os
import re
#import sys
import sqlite3
from datetime import datetime
from tabulate import tabulate
from QueryLib import Query
from read_file import file_reading_gen, nonpy_file_reading_gen


def find_date(dir_path, date=None, pattern=r''):
    """ find the file with the specific date in given dir"""
    if not os.path.isdir(dir_path):
        raise OSError(f'{dir_path} is not a valid directory!')

    for path in os.listdir(dir_path):
        reg = re.search(pattern, path)
        if reg and os.path.isfile(os.path.join(dir_path, path)) and date in path:
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

def my_glob(source_dir, pattern):
    """ Given the directory path and pattern, find all of the file that fit the pattern in this directory."""
    if os.path.isdir(source_dir):
        with os.scandir(source_dir) as it:
            for entry in it:
                fname = entry.name
                reg = re.search(pattern, fname)
                if reg:
                    yield os.path.abspath(os.path.join(source_dir, fname)), reg.group(1)


class System:
    """ Super class for Slate, Blackboard, JSA.
        define the __init__ and other potential shared attr/methods
    """

    def __init__(self, source_dir=None, database=None, pattern=r''):
        """ define the connection path of database, dir path for updating database"""
        self.source_dir = source_dir
        self.database = database
        self.pattern = pattern
    
    def __repr__(self):
        return f'{self.__class__.__name__}(**{self.__dict__})'

    def __str__(self):
        return f'{self.__class__.__name__}'

    def create_table(self):
        """ Create table with proper query"""

    def insert_one_file(self, file_path=None, db_connect=None, date=None):
        """ Insert one specific file into table"""

    def insert_data(self, first_time=False, date=None):
        """ insert data into a table
            if first_time:
                dump all of the data into the database
            if date:
                assumed that there are records in it: need a if statement to check
                only import the specific date.

            first_time and date can not be True at the same time
        """
        if first_time and date:
            raise TypeError("You can't do first_time and date at the same time!")

        connection = sqlite3.connect(self.database)

        if first_time:
            date_dct = dict()
            #date_lst = list()
            for fpath, received_date in my_glob(self.source_dir, self.pattern):
                date_dct[datetime.strptime(received_date, '%y%m%d')] = fpath

            #date_lst = sorted(date_dct.keys())

            for dt in sorted(date_dct.keys()):
                self.insert_one_file(date_dct[dt], connection, dt.strftime('%y%m%d'))

        if date:
            path = find_date(self.source_dir, date, self.pattern)
            self.insert_one_file(path, connection, date)

        connection.close()

    def print_count(self):
        """ Print the counting result group by received_date"""

class Slate(System):
    """ Slate is responsible for generating new Stevens identifications for newly admitted students
        of Steven. There are two general types of students, brand new students and continuing students.
        However there are some continuing students forget to imply that they are former students of
        Stevens and Slate generate a set of new Stevens ID for them.
    """

    def __init__(self, source_dir=None, database=None, pattern=r'sla_([\d]{6})\.csv'):
        super().__init__(source_dir, database, pattern)
        self.create_table()
        
    def create_table(self):
        """ create table Slate in database"""
        connection = sqlite3.connect(self.database)
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

    def print_count(self):
        """ Print the count group by date"""
        connection = sqlite3.connect(self.database)
        cursor = connection.cursor()

        pp_lst = list()
        for row in cursor.execute(Query.summary_slate):
            pp_lst.append(row)

        print('\nSlate information:')
        print(tabulate(pp_lst, headers=['received_date', 'count'], showindex='always', tablefmt='fancy_grid'))
        
        connection.close()

class Blackboard(System):
    """ Blackboard is responsible for providing the data of people who have unified Stevens identification.
        It's used to build the reference for comparsion of the newly admitted students.
    """

    def __init__(self, source_dir=None, database=None, pattern=r'bb_([\d]{6})\.csv'):
        super().__init__(source_dir, database, pattern)
        self.create_table()
        
    def create_table(self):
        """ create table Blackboard in database"""
        connection = sqlite3.connect(self.database)
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

    def print_count(self):
        """ Print the count group by date"""
        connection = sqlite3.connect(self.database)
        cursor = connection.cursor()

        pp_lst = list()
        for row in cursor.execute(Query.summary_bb):
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

    def __init__(self, source_dir=None, database=None, pattern=r'jsa_([\d]{6})\.csv'):
        super().__init__(source_dir, database, pattern)
        self.create_table()

    def create_table(self):
        """ create table JSA in database"""
        connection = sqlite3.connect(self.database)
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

    def print_count(self):
        """ print the count group by date"""
        connection = sqlite3.connect(self.database)
        cursor = connection.cursor()

        pp_lst = list()
        for row in cursor.execute(Query.summary_jsa):
            pp_lst.append(row)

        print('\nJSA information')
        print(tabulate(pp_lst, headers=['received_date', 'count'], showindex='always', tablefmt='fancy_grid'))
        
        connection.close()       

class FacStaff(System):
    """ FacStaff is a system responsible for keeping and maintaining the table of all faculty and staff,
        as when a faculty/staff is a student at the same time, we don't print a student ID card for him/her.
    """

    def __init__(self, source_dir=None, database=None, pattern=r'facsta_([\d]{6})\.csv'):
        super().__init__(source_dir, database, pattern)
        self.create_table()

    def create_table(self):
        """ Create a table FacStaff in database."""
        connection = sqlite3.connect(self.database)
        connection.execute(Query.create_facsta)
        connection.commit()
        connection.close()
    
    def insert_one_file(self, file_path=None, db_connect=None, date=None):
        """ Insert one specific file into table"""
        if not db_connect:
            raise ConnectionError('No connection of database provided!')
        
        cursor = db_connect.cursor()

        for emp_id, full_name, work_name, cwid, email, phone, \
            non0, non1, non2, non3, non4, non5, non6, non7, non8, non9, non10, non11, non12 \
            in nonpy_file_reading_gen(file_path, 19, header=True):

            name = work_name.strip().split(' ')
            first = name[0]
            last = name[-1]
            middle = '' if len(name) <= 2 else ' '.join(name[1: -1])

            data = (cwid, first, middle, last, email, phone, date)
            cursor.execute(Query.insert_facsta, data)
        
        db_connect.commit()

    def print_count(self):
        """ print the count group by date"""
        connection = sqlite3.connect(self.database)
        cursor = connection.cursor()

        pp_lst = list()
        for row in cursor.execute(Query.summary_facsta):
            pp_lst.append(row)

        print('\nFacStaff information')
        print(tabulate(pp_lst, headers=['received_date', 'count'], showindex='always', tablefmt='fancy_grid'))
        
        connection.close()     

class StudentInfo(System):
    """ StudentInfo is responsible for recording all of the enrolled students for each semester"""

    def __init__(self, source_dir, database, pattern=r'sis_([\d]{6})\.csv'):
        super().__init__(source_dir, database, pattern)
        self.create_table()

    def create_table(self):
        """ Create the 18F enrolld students table."""
        connection = sqlite3.connect(self.database)
        connection.execute(Query.create_sis)
        connection.commit()
        connection.close()

    def insert_one_file(self, file_path=None, db_connect=None, date=None):
        """ Insert one specific file into table"""
        if not db_connect:
            raise ConnectionError('No connection of database provided!')
        
        cursor = db_connect.cursor()

        for name, cwid, stevens_e, personal_e, non0, non1, exit_term, level, non2, non3 \
            in nonpy_file_reading_gen(file_path, 10, header=True):
            names = name.strip().split(',')
            last = names[0].strip()
            first = '' if len(names) <= 1 else ' '.join(names[1:])

            data = (cwid, first, last, stevens_e, personal_e, exit_term, level, date)
            cursor.execute(Query.insert_sis, data)
        
        db_connect.commit()

    def print_count(self):
        """ print the count group by date"""
        connection = sqlite3.connect(self.database)
        cursor = connection.cursor()

        pp_lst = list()
        for row in cursor.execute(Query.summary_sis):
            pp_lst.append(row)

        print('\nFacStaff information')
        print(tabulate(pp_lst, headers=['level', 'count'], showindex='always', tablefmt='fancy_grid'))
        
        connection.close()       


def main():
    """ for test"""
    
    TODAY = datetime.today().strftime('%y%m%d')
    DUCKCARD = os.path.join(os.pardir, 'DuckCard_data')

    data_source = os.path.join(DUCKCARD, 'data_source')
    #db = os.path.join(DUCKCARD, 'duckcard_DB.db')  
    db = os.path.join(os.curdir, 'duckcard.db')  # for test and debug

    sla = Slate(data_source, db)
    sla.insert_data(first_time=True)  # date=TODAY
    sla.print_count()

    bb = Blackboard(data_source, db)
    #bb.insert_data(date=TODAY)  # date=TODAY first_time=True
    #bb.print_count()

    jsa = JSA(data_source, db)
    jsa.insert_data(first_time=True)  # first_time=True
    jsa.print_count()

    facsta = FacStaff(data_source, db)
    facsta.insert_data(first_time=True)  # date=TODAY
    facsta.print_count()

    sis = StudentInfo(data_source, db)
    sis.insert_data(first_time=True) # date=TODAY
    sis.print_count()
    print("")

if __name__ == '__main__':
    main()
