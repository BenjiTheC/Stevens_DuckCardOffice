""" 
Input the date range
extract all of the Export_[exportedDate]
combine them into one .csv file

- Basically this script is only applicable under this specific repo, fuck open source :)
- However, I will try to implement it to be compatible for Window OS

Here is how this script will work:
- given a date range
- Scan the current dir '.'(not a emoji) with os
- locate every directory with names 'Export_[exportedDate]'
- go into this directory, find the file 'con_[exportedDate].csv', readit
- put all content into one file
    
"""

import os
import sys
import re
from read_file import file_reading_gen

def traverse_dir(dir_path=os.curdir, pattern=r'^Export_([\d]{4})'):
    """ 
    given a directory path, traverse and find the naem with pattern included
    by default searching for current directory and patter as r'Export_([\d]{4})'
    """

    if not os.path.isdir(dir_path):             # validate the directory
        raise OSError(f"\nThe directory {dir_path} doesn't exist!\n")

    lst_to_write = list()
    dir_list = os.listdir(dir_path)

    for file_ in dir_list:
        if re.search(pattern, file_) and os.path.isdir(file_):           # it's a directory and the one we are finding
            lst_to_write.extend(dive_and_find(file_))
    
    return lst_to_write

def dive_and_find(directory, pattern=r'^con_([\d]{4}).*\.csv$'):
    """ open a directory (change directory), find 'con_[exportedDate]' and return a list of result
        element of return list:
            a list: [cwid, first, middle, last, date]
    """
    lst_to_write = list()

    origin = os.path.abspath(os.curdir)     # mark the original directory

    os.chdir(directory)

    dir_list = os.listdir(os.curdir)
    for file_ in dir_list:
        if re.search(pattern, file_):       # we have found what we want

            date = re.search(pattern, file_).group(1)
            for cwid, first, middle, last in file_reading_gen(file_, 4, header=True):
                lst_to_write.append([cwid, first, middle, last, f'{date[:2]}/{date[2:]}'])

    os.chdir(origin)                # go back to where we start
    return lst_to_write

def wirte_file(lst_to_wrtie):
    """ write the row into the file"""
    try:
        fwrite = open('all_cons.csv', 'w')
    except FileExistsError:
        raise FileExistsError(f'\nFile already exist.\n')
    else:
        fwrite.write('CWID,First,Middle,Last,Date\n')       # write the header
        
        for row in lst_to_wrtie:
            fwrite.write(','.join(row)+'\n')
        else:
            print('\nwriting complete\n')

def main():
    """ Entrance of program"""

    lst_to_write = traverse_dir()
    wirte_file(lst_to_write)

if __name__ == "__main__":
    main()