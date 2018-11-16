"""
Input: a tabular data of newly admitted students
Output: a tabular data of students who already have a record in the database
"""
from collections import defaultdict
import pandas as pd 
import tabulate

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

def campus_personnel(filepath):
    """ Big dataset for comparison"""
    incampus = dict()               # key: (first, middle, last) value: cwid

    for cwid, first, middle, last, uggr, exp in file_reading_gen(filepath, 6, header= True):
        name = (first.strip().lower(), middle.strip().lower(), last.strip().lower())
        incampus[name] = cwid.strip()

    return incampus

def newly_admitted(filepath):
    """ Check if the person in file is in the datadict"""
    newad = dict()                # key: name  value: cwid
    for cwid, first, middle, last, username, email, dcisionfn, pround, defer, dcisionln, exp, uggr in file_reading_gen(filepath, 12, header= True):
        name = (first.strip().lower(), middle.strip().lower(), last.strip().lower())
        newad[name] = cwid.strip()

    return newad

def find_repeat(incampus: dict, newad: dict):
    """ find repeat personnel"""

    suspect = dict()
    continuing = dict()
    brand_new = dict()

    for name, cwid in newad.items():
        if name in incampus:            # same name --> possibly same person, check cwid
            if cwid == incampus[name]:      # same cwid --> continuing student, no problem
                continuing[name] = cwid
            else:                           # diff cwid --> suspect
                suspect[name] = {'newID': cwid, 'oldID': incampus[name]}

        else:                           # different name --> difinitely brand new
            brand_new[name] = cwid

    return suspect, continuing, brand_new
    

def main():
    dataset_path = "/Users/benjamin/Documents/Campus_Card_Office/photo_upload/CampusPersonnel.csv"
    
    test_path = "/Users/benjamin/Documents/Campus_Card_Office/photo_upload/Newly_admitted.csv"
    newlyadmit_path = "/Users/benjamin/Documents/Campus_Card_Office/photo_upload/Newly_Admitted_20181106.csv"

    incampus = campus_personnel(dataset_path)
    newad = newly_admitted(newlyadmit_path)
    suspect, contiuning, brand_new = find_repeat(incampus, newad)


    print(f'\nSuspect:')
    pd_sus = pd.DataFrame.from_dict(suspect, orient= 'index')
    #print(tabulate.tabulate(suspect, headers= ['Name', 'newCWID', 'oldCWID'], tablefmt="fancy_grid"))
    
    print(f'\nContinuing:')
    pd_con = pd.DataFrame.from_dict(contiuning, orient= 'index')
    print(tabulate.tabulate(pd_con, headers= ['Name', 'CWID'], tablefmt= "fancy_grid"))
    
    print(f'\nBrand New:')
    pd_new = pd.DataFrame.from_dict(brand_new, orient= 'index')
    print(tabulate.tabulate(pd_new, headers= ['Name', 'CWID'], tablefmt= "fancy_grid"))

    print(f'\ntotal students: {len(suspect) + len(contiuning) + len(brand_new)}')

   
    
    


    

if __name__ == "__main__":
    main()