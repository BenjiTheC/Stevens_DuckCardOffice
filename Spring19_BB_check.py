"""
Given a Excel file from Slate, recognized if each of the student is in the BlackBoard Excersice.

Process:
- Received the Excel file, save as .csv.
- Eliminate whitespace in the 'First' column, make 'First', 'Middle', 'Last' uppercase.
- Build a table in the database for the particular file.
- Cross check the database to separate students in the file into 
    Brand_New_[exportdate].csv, Continuing[exportdate], Suspect[exportdate]
"""

import os
import sys
import sqlite3

# File reading generator
def file_reading_gen(path, fields, sep = ',', header = False):
    """ A generator that reads text files and returns all of the values on a single line on each call to next()"""
    try:
        open_file = open(path, 'r')
    except FileNotFoundError:
        raise FileNotFoundError("{0} can't be found or opened".format(path))
    else:
        with open_file:

            for ind, line in enumerate(open_file):
                if header:
                    header = False
                    continue

                res = line.rstrip('\n').split(sep)

                if len(res) != fields:               # raise ValueError if the fields don't match
                    raise ValueError(f"{path} has {len(res)} fields in line {ind} but expected {fields}")

                yield tuple(res)


class ExistenceCheck:
    """ 
    Technical solution for identifying the newly admitted students for Stevens
    ====================================================================================================

    Input:
    Two .csv files. 
    One as reference of all the in-campus personnel, another as the new students need to be identified.

    Output:
    Three .csv files.
    - brn_[exported_date]: confirmed brand new students' info. Send this to IT/GradAdm
    - con_[exported_date]: confirmed continuing students' info. Update their UG/GR and ExitDate.
    - sus_[exported_date]: uncertain students who may be brand new or continuing, check with Ms. Edge.
    
    ----------------------------------------------------------------------------------------------------
    
    Solution Details:
    
    - Database:
    Use Sqlite in-memory database for data manipulation and searching solution, abandon the database on- 
    ce the cross-checking operation is finished. No .db file needed.

        Three tables will be created in the database:
        - campus: 
            (
                CWID TEXT, First TEXT, Middle TEXT, Last TEXT
            )
            All in-campus personnel's info, names separated into 3 fields, all UPPERCASE written.
            The original file is exported from BlackBoard DataBase

        - newad[exported_date]:
            (
                CWID TEXT, First TEXT, Middle TEXT, Last TEXT
            )
            All newly admitted students' info, names separated into 3 fields, all UPPERCASE written.
            The original file is exported from Slate DataBase, all info entered by applicants personally.

        - raw_newad[exported_date]:
            (
                CWID TEXT, First TEXT, Middle TEXT, Last TEXT
            )
            A talbe created from the same file as newad[exported_date], for sending to the IT Dept for 
            BlackBoard Database update.
        
        - The first two tables are created for finding the continuing students and suspect students, by sus-
        pects it mean this student can NOT be identified as either brand new or continuing, manually check
        needed. The last table is used to write the original names for the newly admitted students
        
    - SQL statements needed in the scripts:

        /* suspect */
        select distinct newad.CWID, newad.First, newad.Middle, newad.Last  from  newad newad
        join campus cp
            on newad.First = cp.First
            and newad.Last = cp.Last
            and not (cp.Middle != newad.Middle and cp.Middle != '' and newad.Middle != '')
        where cp.CWID != newad.CWID;

        /* continuing */
        select distinct newad.CWID, newad.First, newad.Middle, newad.Last
        from newad newad
        join campus cp
            on newad.CWID = cp.CWID
        ;

        /* brand new */
        select distinct raw.CWID, raw.First, raw.Middle, raw.Last
        from raw_newad raw
        where raw.CWID not in
        (
        /* suspect */
            select distinct newad.CWID
            from newad newad
            join campus cp
                on newad.First = cp.First
                and newad.Last = cp.Last
                and not (cp.Middle != newad.Middle and cp.Middle != '' and newad.Middle != '')
            where cp.CWID != newad.CWID

        union

        /* continuing */
            select distinct newad.CWID
            from newad newad
            join campus cp
                on newad.CWID = cp.CWID

        )

    - Attributes:
        - Paths for two .csv files: 
            Given by the user.
        - connection object created in __init__:
            Place to create tables, execute SQL.
    
    - Basic methods:
      - __init__(self, campus_path, newad_path)

      - build_reference():
            create the 3 tables from the file, call campus_modify(), newad_modify() for the fixed info

      - find_brnsuscon():
            find and write brand new, continuing, suspect students into the new files.

      - campus_modify() and newad_modify():
            generators for writing adjusted data, they are separated into two because the fields for two
            files are different.

      - exported_date():
            extract the exported_date and apply it into the file written and database table name
    
    """

    def __init__(self, campus_path, newad_path):
        self.campus_path = campus_path
        self.newad_path = newad_path

        if self._is_file(self.campus_path) and self._is_file(self.newad_path):
            
            self._exported_date = self._extract_date()

            # cerate the connection to database:
            self._connection = sqlite3.connect(":memory:")

            self._build_reference()
            self._find_brnsuscon()
            
            print("Process complete!\nClosing the database.")
            self._connection.close()
            print("Database closed, see you next time.")

    def _is_file(self, filepath):
        """ Validate the two file paths."""

        if os.path.isfile(filepath):
            
            print(f"{filepath} exist.")
            if not filepath.endswith('.csv'):
                # not a .csv file but may be .txt in a csv form writting.
                print(f"\nWARNING: {filepath} is not a .csv file, may not be ligit for database building! Please double check the file!\n")
            
            return True

        else:
            raise OSError(f"{filepath} is NOT a file!")

    def _build_reference(self):
        """
        Input base table into the database
        - InCampusPersonnel.csv --> read_modify() --> table 'campus'
        - Newly_Adimitted_[exportdate].csv --> read_modify() --> talbe 'newad[exportdate]'
        """  

        connection = self._connection
        
      # create table 'campus' in the database
        campus = connection.cursor()
        
        tbl_campus = """CREATE TABLE campus
                        (
                            CWID TEXT,
                            First TEXT,
                            Middle TEXT,
                            Last TEXT
                        )"""
        campus.execute(tbl_campus)

        insert_campus = """ INSERT INTO campus (CWID, First, Middle, Last)
                            VALUES (?, ?, ?, ?);"""
        for data in self._campus_modify():      # data: (cwid, first, middle, last) all UPPERCASE
            campus.execute(insert_campus, data)

        update_campus = """UPDATE campus SET Middle = '' WHERE Middle = '{NULL}'"""
        campus.execute(update_campus)   # eliminate '{NULL}' string in the middle name

      # create table 'newad' in the database --> for con and sus
        newad = connection.cursor()
        
        tbl_newad = """CREATE TABLE newad
                        (
                            CWID TEXT,
                            First TEXT,
                            Middle TEXT,
                            Last TEXT
                        )"""
        newad.execute(tbl_newad)

        insert_newad = """ INSERT INTO newad (CWID, First, Middle, Last)
                            VALUES (?, ?, ?, ?);"""
        for data in self._newad_modify():      # data: (cwid, first, middle, last) all UPPERCASE
            newad.execute(insert_newad, data)
        
      # create table 'raw_campus' in the database -> for brn
        raw_newad = connection.cursor()

        tbl_raw = """CREATE TABLE raw_newad
                    (
                        CWID TEXT,
                        First TEXT,
                        Middle TEXT,
                        Last TEXT
                    )"""
        raw_newad.execute(tbl_raw)

        insert_raw = """ INSERT INTO raw_newad (CWID, First, Middle, Last)
                        VALUES (?, ?, ?, ?);"""
        for cwid, first, middle, last, username, email, dcisionfn, prnd, defer, dcisionln, pchange, special in file_reading_gen(self.newad_path, 12, header= True):
            raw_newad.execute(insert_raw, (cwid, first, middle, last))
    
      # output the database table counts
        for num in connection.execute("SELECT COUNT(*) FROM campus"):
            cnt_campus = num

        for num in connection.execute("SELECT COUNT(*) FROM newad"):
            cnt_newad = num

        for num in connection.execute("SELECT COUNT(*) FROM raw_newad"):
            cnt_raw = num

        print(f"campus count: {cnt_campus}\nnewad count: {cnt_newad}\nraw count: {cnt_raw}")
      # connection close
        connection.commit()
    
    def _campus_modify(self):
        """ A GENERATOR\nRead the file and eliminate the whitespace and return a f-string with tuples that have the 4 fields"""
        for cwid, first, middle, last, uggr, exp in file_reading_gen(self.campus_path, 6, header= True):
            first = first.strip().split(' ')[0]
            yield (cwid, first.upper(), middle.upper(), last.upper())

    def _newad_modify(self):
        """ A GENERATOR\nRead the file and eliminate the whitespace and return a f-string with tuples that have the 4 fields"""
        for cwid, first, middle, last, username, email, dcisionfn, prnd, defer, dcisionln, pchange, special in file_reading_gen(self.newad_path, 12, header= True):
            first = first.strip().split(' ')[0]
            yield (cwid, first.upper(), middle.upper(), last.upper())

    def _find_brnsuscon(self):
        """ Find the brandnew, continuing, suspect students"""
        
        connection = self._connection
      # find and write continuing
        con = connection.cursor()
        find_con = """select distinct newad.CWID, newad.First, newad.Middle, newad.Last
                    from newad newad
                    join campus cp
                        on newad.CWID = cp.CWID"""

        with open(f'con_{self._exported_date}.csv', 'w') as fwrite:
            fwrite.write(f"CWID,First,Middle,Last\n")

            for cwid, first, middle, last in con.execute(find_con):
                fwrite.write(f"{cwid},{first},{middle},{last}\n")

      # find and write suspects
        sus = connection.cursor()
        find_sus = """select distinct newad.CWID, newad.First, newad.Middle, newad.Last  
                      from  newad newad
                      join campus cp
                        on newad.First = cp.First
                        and newad.Last = cp.Last
                        and not (cp.Middle != newad.Middle and cp.Middle != '' and newad.Middle != '')
                      where cp.CWID != newad.CWID"""

        with open(f'sus_{self._exported_date}.csv', 'w') as fwrite:
            fwrite.write(f"CWID,First,Middle,Last\n")

            for cwid, first, middle, last in sus.execute(find_sus):
                print(f"writing\t{cwid}, {first}, {middle}, {last}\tinto the file.")
                fwrite.write(f"{cwid},{first},{middle},{last}\n")
        
      # find and write brandnew
        brn = connection.cursor()
        find_brn = """select distinct raw.CWID, raw.First, raw.Middle, raw.Last
                    from raw_newad raw
                    where raw.CWID not in
                    (
                    
                        select distinct newad.CWID
                        from newad newad
                        join campus cp
                            on newad.First = cp.First
                            and newad.Last = cp.Last
                            and not (cp.Middle != newad.Middle and cp.Middle != '' and newad.Middle != '')
                        where cp.CWID != newad.CWID

                        union

                    
                        select distinct newad.CWID
                        from newad newad
                        join campus cp
                            on newad.CWID = cp.CWID

                    )"""
        
        with open(f'brn_{self._exported_date}.csv', 'w') as fwrite:
            uggr = 'GR'
            exdate = '12/31/2022'
            fwrite.write(f"CWID,First,Middle,Last,UG/GR,ExitDate\n")

            for cwid, first, middle, last in brn.execute(find_brn):
                fwrite.write(f"{cwid},{first},{middle},{last},{uggr},{exdate}\n")

    def _extract_date(self):
        """ Analyze and extract the exported date from self.newad_path file name"""
        if self.newad_path[-8:-4].isdigit():
            return self.newad_path[-8:-4]
        else:
            return "undated"

def main():
    campuspath = "./InCampusPersonnel.csv"
    newadpath = input("Parse your newly admitted student list file FULL PATH here:\n")

    ExistenceCheck(campuspath, newadpath)

if __name__ == "__main__":
    main()

