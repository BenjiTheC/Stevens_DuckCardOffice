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

def build_reference(campuspath, newadpath):
    """
    Input base table into the database
      - InCampusPersonnel.csv --> read_modify() --> table 'campus'
      - Newly_Adimitted_[exportdate].csv --> read_modify() --> talbe 'newad[exportdate]'
    """  

    connection = sqlite3.connect("/Users/benjamin/Documents/Campus_Card_Office/photo_upload/19Spring_brnconsus.db")
    
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
    for data in campus_modify(campuspath):      # data: (cwid, first, middle, last) all UPPERCASE
        campus.execute(insert_campus, data)

    update_campus = """UPDATE campus SET Middle = '' WHERE Middle = '{NULL}'"""
    campus.execute(update_campus)   # eliminate '{NULL}' string in the middle name

   # create table 'newad[exportdate]' in the database --> for con and sus
    newad = connection.cursor()
    
    tbl_newad = """CREATE TABLE newad_1108
                    (
                        CWID TEXT,
                        First TEXT,
                        Middle TEXT,
                        Last TEXT
                    )"""
    newad.execute(tbl_newad)

    insert_newad = """ INSERT INTO newad_1108 (CWID, First, Middle, Last)
                        VALUES (?, ?, ?, ?);"""
    for data in newad_modify(newadpath):      # data: (cwid, first, middle, last) all UPPERCASE
        newad.execute(insert_newad, data)
    
   # create table 'raw_campus' in the database -> for brn
    raw_newad = connection.cursor()

    tbl_raw = """CREATE TABLE raw_newad_1108
                (
                    CWID TEXT,
                    First TEXT,
                    Middle TEXT,
                    Last TEXT
                )"""
    raw_newad.execute(tbl_raw)

    insert_raw = """ INSERT INTO raw_newad_1108 (CWID, First, Middle, Last)
                     VALUES (?, ?, ?, ?);"""
    for cwid, first, middle, last, username, email, dcisionfn, pround, defer, dcisionln, pchange, special in file_reading_gen(newadpath, 12, header= True):
        raw_newad.execute(insert_raw, (cwid, first, middle, last))
   
   # output the database table counts
    for num in connection.execute("SELECT COUNT(*) FROM campus"):
        cnt_campus = num

    for num in connection.execute("SELECT COUNT(*) FROM newad_1108"):
        cnt_newad = num

    for num in connection.execute("SELECT COUNT(*) FROM raw_newad_1108"):
        cnt_raw = num

    print(f"campus count: {cnt_campus}\nnewad count: {cnt_newad}\nraw count: {cnt_raw}")
   # connection close
    connection.commit()
    connection.close()

def find_brnsuscon():
    """ Find the brandnew, continuing, suspect students"""
    
    connection = sqlite3.connect("/Users/benjamin/Documents/Campus_Card_Office/photo_upload/19Spring_brnconsus.db")
   # find and write continuing
    con = connection.cursor()
    find_con = """select distinct newad.CWID, newad.First, newad.Middle, newad.Last
                  from newad_1108 newad
                  join campus cp
                    on newad.CWID = cp.CWID"""

    with open('con_1108.csv', 'w') as fwrite:
        fwrite.write(f"CWID,First,Middle,Last\n")

        for cwid, first, middle, last in con.execute(find_con):
            fwrite.write(f"{cwid},{first},{middle},{last}\n")

   # find and write suspects
    sus = connection.cursor()
    find_sus = """select distinct newad.CWID, newad.First, newad.Middle, newad.Last  from  newad_1108 newad
                  join campus cp
                    on newad.First = cp.First
                    and newad.Last = cp.Last
                    and not (cp.Middle != newad.Middle and cp.Middle != '' and newad.Middle != '')
                  where cp.CWID != newad.CWID"""

    with open('sus_1108.csv', 'w') as fwrite:
        fwrite.write(f"CWID,First,Middle,Last\n")

        for cwid, first, middle, last in sus.execute(find_sus):
            print(f"writing\t{cwid}, {first}, {middle}, {last}\tinto the file.")
            fwrite.write(f"{cwid},{first},{middle},{last}\n")
    
   # find and write brandnew
    brn = connection.cursor()
    find_brn = """select distinct raw.CWID, raw.First, raw.Middle, raw.Last
                  from raw_newad_1108 raw
                  where raw.CWID not in
                  (
                
                    select distinct newad.CWID
                    from newad_1108 newad
                    join campus cp
                        on newad.First = cp.First
                        and newad.Last = cp.Last
                        and not (cp.Middle != newad.Middle and cp.Middle != '' and newad.Middle != '')
                    where cp.CWID != newad.CWID

                    union

                
                    select distinct newad.CWID
                    from newad_1108 newad
                    join campus cp
                        on newad.CWID = cp.CWID

                  )"""
    
    with open('brn_1108.csv', 'w') as fwrite:
        uggr = 'GR'
        exdate = '12/31/2022'
        fwrite.write(f"CWID,First,Middle,Last,UG/GR,ExitDate\n")

        for cwid, first, middle, last in brn.execute(find_brn):
            fwrite.write(f"{cwid},{first},{middle},{last},{uggr},{exdate}\n")

    connection.close()

def campus_modify(filepath):
    """ A GENERATOR\nRead the file and eliminate the whitespace and return a f-string with tuples that have the 4 fields"""
    for cwid, first, middle, last, uggr, exp in file_reading_gen(filepath, 6, header= True):
        first = first.strip().split(' ')[0]
        yield (cwid, first.upper(), middle.upper(), last.upper())

def newad_modify(filepath):
    """ A GENERATOR\nRead the file and eliminate the whitespace and return a f-string with tuples that have the 4 fields"""
    for cwid, first, middle, last, username, email, dcisionfn, pround, defer, dcisionln, pchange, special in file_reading_gen(filepath, 12, header= True):
        first = first.strip().split(' ')[0]
        yield (cwid, first.upper(), middle.upper(), last.upper())

def main():
    campuspath = "/Users/benjamin/Documents/Campus_Card_Office/photo_upload/InCampusPersonnel.csv"
    newadpath = "/Users/benjamin/Documents/Campus_Card_Office/photo_upload/Export_1108/Export_1106-08.csv"

    build_reference(campuspath, newadpath)
    find_brnsuscon()

if __name__ == "__main__":
    main()

