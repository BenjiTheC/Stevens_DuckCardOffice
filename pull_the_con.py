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

def traverse_dir(dir_path=os.curdir, pattern=r'Export_([\d]{4})'):
    """ 
    given a directory path, traverse and find the naem with pattern included
    by default searching for current directory and patter as r'Export_([\d]{4})'
    """

    if not os.path.isdir(dir_path):             # validate the directory
        raise OSError(f"\nThe directory {dir_path} doesn't exist!\n")

    with open('all_cons.csv', 'a+') as fwrite:
        dir_list = os.listdir(dir_path)

        for a_dir in dir_list:
            if re.search(pattern, a_dir):           # it's the directory we are finding
                pass

def dive_find_write(directory):
    """ open a directory (change directory), find 'con_[exportedDate]' and return a file object"""

    pass
