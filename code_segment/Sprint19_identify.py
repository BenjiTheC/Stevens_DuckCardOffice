""" distinguish error prone information from received Slate report"""

import os
import sqlite3
import re
from read_file import file_reading_gen

IN_CAMPUS_PERSONNEL = '/Users/benjamin/Documents/Campus_Card_Office/DuckCard_data/InCampusPersonnel'
RAW_EXPORT = '/Users/benjamin/Documents/Campus_Card_Office/DuckCard_data/errorDistinguish/rawExport'
BRN = '/Users/benjamin/Documents/Campus_Card_Office/DuckCard_data/errorDistinguish/brn'
CON = '/Users/benjamin/Documents/Campus_Card_Office/DuckCard_data/errorDistinguish/con'
SUS = '/Users/benjamin/Documents/Campus_Card_Office/DuckCard_data/errorDistinguish/sus'

def is_file(filepath):
    """ Validate the two file paths."""

    if os.path.isfile(filepath):
        
        print(f"{filepath} exist.")
        if not filepath.endswith('.csv'):
            # not a .csv file but may be .txt in a csv form writting.
            print(f"\nWARNING: {filepath} is not a .csv file, may not be ligit for database building! Please double check the file!\n")
        
        return True

    else:
        raise OSError(f"{filepath} is NOT a file!")


class ExistenceCheck:
    """ Distinguish error prone information in newly admitted students data 

        Input: 2 .csv files. 
        - InCampusPersonnel.csv: reference of all the in-campus personnel.
        - Export_[exported_date]: the new students need to be identified.

        Output: 3 .csv files.
        - brn_[exported_date]: confirmed brand new students' info. Send this to IT/GradAdm.
        - con_[exported_date]: confirmed continuing students' info. Update their UG/GR and ExitDate.
        - sus_[exported_date]: uncertain students who may be brand new or continuing, check with Ms. Edge.

        Process:
        - Received the Excel file, save as .csv.
        - Eliminate whitespace in the 'First' column, make 'First', 'Middle', 'Last' uppercase.
        - Build a table in the database for the particular file.
        - Cross check the database to separate students in the file into
    """

    def __init__(self, campus_path, newad_path, in_memory=True):
        self.campus_path = campus_path
        self.newad_path = newad_path

        if is_file(self.campus_path) and is_file(self.newad_path):
            
            self._exported_date = self._extract_date()
            self._connection = sqlite3.connect(':memory:' if in_memory else 'for_debug.db')           

            self._build_reference()
            self._insert_data()
            self._find_brnsuscon()

            self._connection.close()

    def _build_reference(self):
        """ Build the tables"""  

        cursor = self._connection.cursor()   
        query_tbl_campus =\
            """ CREATE TABLE campus
                (
                    CWID TEXT,
                    First TEXT,
                    Middle TEXT,
                    Last TEXT
                )
            """

        query_tbl_newad =\
            """ CREATE TABLE newad
                (
                    CWID TEXT,
                    First TEXT,
                    Middle TEXT,
                    Last TEXT
                )
            """

        query_tbl_raw =\
            """ CREATE TABLE raw_newad
                (
                    CWID TEXT,
                    First TEXT,
                    Middle TEXT,
                    Last TEXT
                )
            """

        for query in query_tbl_campus, query_tbl_newad, query_tbl_raw:
            cursor.execute(query)

        self._connection.commit()

    def _insert_data(self):
        """ read the file and insert the data into the file
              - InCampusPersonnel.csv --> read_modify() --> table 'campus'
              - Newly_Adimitted_[exportdate].csv --> read_modify() --> talbe 'newad[exportdate]'
        """
        cursor = self._connection.cursor()

        query_add_campus = """ INSERT INTO campus (CWID, First, Middle, Last)
                               VALUES (?, ?, ?, ?);"""
        
        query_upd_campus = """ UPDATE campus SET Middle = '' WHERE Middle = '{NULL}'"""

        query_add_newad = """ INSERT INTO newad (CWID, First, Middle, Last)
                              VALUES (?, ?, ?, ?);"""

        query_add_raw = """ INSERT INTO raw_newad (CWID, First, Middle, Last)
                            VALUES (?, ?, ?, ?);"""

        # insert into campus
        for data in self._campus_modify():
            cursor.execute(query_add_campus, data)

        cursor.execute(query_upd_campus)  # eliminate '{NULL}' string in the middle name  

        # insert into newad
        for data in self._newad_modify():
            cursor.execute(query_add_newad, data)
        
        # insert into raw
        for cwid, first, middle, last, username, email, dcisionfn, prnd, defer, dcisionln, pchange, special \
            in file_reading_gen(self.newad_path, 12, header=True):
            data = (cwid, first, middle, last)
            cursor.execute(query_add_raw, (cwid, first, middle, last))
        
        self._connection.commit()
        
        # output the database table counts
        for num in cursor.execute("SELECT COUNT(*) FROM campus"):
            cnt_campus = num

        for num in cursor.execute("SELECT COUNT(*) FROM newad"):
            cnt_newad = num

        for num in cursor.execute("SELECT COUNT(*) FROM raw_newad"):
            cnt_raw = num

        print(f"campus count: {cnt_campus}\nnewad count: {cnt_newad}\nraw count: {cnt_raw}")
    
    def _campus_modify(self):
        """ A GENERATOR\nRead the file and eliminate the whitespace and return a f-string with tuples that have the 4 fields"""
        for cwid, first, middle, last, uggr, exp in file_reading_gen(self.campus_path, 6, header=True):
            first = first.strip().split(' ')[0]
            yield (cwid, first.upper(), middle.upper(), last.upper())

    def _newad_modify(self):
        """ A GENERATOR\nRead the file and eliminate the whitespace and return a f-string with tuples that have the 4 fields"""
        for cwid, first, middle, last, username, email, dcisionfn, prnd, defer, dcisionln, pchange, special in file_reading_gen(self.newad_path, 12, header=True):
            first = first.strip().split(' ')[0]
            yield (cwid, first.upper(), middle.upper(), last.upper())

    def _find_brnsuscon(self):
        """ Find the brandnew, continuing, suspect students"""
        
        cursor = self._connection.cursor()

        find_con =\
            """ select distinct newad.CWID, newad.First, newad.Middle, newad.Last
                from newad newad
                join campus cp
                  on newad.CWID = cp.CWID
            """


        find_sus =\
            """ select distinct newad.CWID, newad.First, newad.Middle, newad.Last  
                from newad newad
                join campus cp
                  on newad.First = cp.First
                  and newad.Last = cp.Last
                  and not (cp.Middle != newad.Middle and cp.Middle != '' and newad.Middle != '')
                where cp.CWID != newad.CWID
                  and newad.CWID not in (
                    select distinct newad.CWID
                    from newad newad
                    join campus cp
                    on newad.CWID = cp.CWID
                    )
            """

        find_brn =\
            """ select distinct raw.CWID, raw.First, raw.Middle, raw.Last
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
                      and newad.CWID not in (
                        select distinct newad.CWID
                        from newad newad
                        join campus cp
                          on newad.CWID = cp.CWID
                    )

                    union

                
                    select distinct newad.CWID
                    from newad newad
                    join campus cp
                      on newad.CWID = cp.CWID

                )
            """

        if list(cursor.execute(find_con)):

            with open(os.path.join(CON, f'con_{self._exported_date}.csv'), 'w') as fwrite:
                fwrite.write(f"CWID,First,Middle,Last\n")

                for cwid, first, middle, last in cursor.execute(find_con):
                    fwrite.write(f"{cwid},{first},{middle},{last}\n")

        else:
            print('No continuing student.')


        if list(cursor.execute(find_sus)):
        
            with open(os.path.join(SUS, f'sus_{self._exported_date}.csv'), 'w') as fwrite:
                fwrite.write(f"CWID,First,Middle,Last\n")

                for cwid, first, middle, last in cursor.execute(find_sus):
                    print(f"writing\t{cwid}, {first}, {middle}, {last}\tinto the file.")
                    fwrite.write(f"{cwid},{first},{middle},{last}\n")

        else:
            print('No suspect student.')
        

        with open(os.path.join(BRN, f'brn_{self._exported_date}.csv'), 'w') as fwrite:
            fwrite.write(f"CWID,First,Middle,Last,UG/GR,ExitDate\n")
            
            uggr, exdate = 'GR', '12/31/2022'

            for cwid, first, middle, last in cursor.execute(find_brn):
                fwrite.write(f"{cwid},{first},{middle},{last},{uggr},{exdate}\n")

    def _extract_date(self):
        """ Analyze and extract the exported date from self.newad_path file name"""
        pattern = r'Export_([\d]{4})\.csv'
        if re.search(pattern, self.newad_path):
            return re.search(pattern, self.newad_path).group(1)
        else:
            return "undated"

def main():
    """ Entrance"""
    campuspath = os.path.join(IN_CAMPUS_PERSONNEL, 'InCampusPersonnel.csv')
    newadpath = os.path.join(RAW_EXPORT, input('parse your file name: ') + '.csv')

    ExistenceCheck(campuspath, newadpath)   #os.path.join(os.curdir, newadpath, newadpath + '.csv')

if __name__ == "__main__":
    main()
