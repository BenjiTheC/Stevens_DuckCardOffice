"""
Given the newest data from Blackboard, 
double check if the brn_[exporteddate] students are successfully imported

"""

import os
import sys

def csv_yield_one_field(filepath, fields: int, sep=',', header=False, field_to_yield=0):
    """
    Generator
    ================================================================================
    Only read the first field in a separated value file
    yield it
    """
    if field_to_yield > fields - 1:
        raise ValueError(f"You try to yield {field_to_yield}th field with a file only has {fields} fields!")

    try:
        openfile = open(filepath, 'r')
    except FileNotFoundError:
        raise FileNotFoundError(f"The file {filepath} doesn't exist!")
    else:

        with openfile:
            for ind, line in enumerate(openfile):
                
                if header:              # skip the header
                    header = False
                    continue
                
                res = line.rstrip('\n\r').split(sep)   # res list, yield a specific element from here

                if len(res) != fields:
                    raise ValueError(f"{filepath} has {len(res)} fields in line {ind} but expected {fields}!")

                yield res[field_to_yield]

def check_exist(cmpr: list, base: list, item_name='CWID'):
    """ check if the elements in list cmpr are also in the base"""
    
    not_in_base = list()

    for item in cmpr:
        if item not in base:
            not_in_base.append(item)
            print(f"{item_name} {item} is NOT in the base data.")
    
    if not not_in_base:
        print(f"All of the {item_name} in cmpr are in the base.")
        

def main():
    base_file = "/Users/benjamin/Documents/Campus_Card_Office/Stevens_DuckCardOffice/InCampusPersonnel_1115.csv"
    compare_file = "/Users/benjamin/Documents/Campus_Card_Office/Stevens_DuckCardOffice/Export_1108/brn_1108.csv"

    base_lst = list(csv_yield_one_field(base_file, 6, header= True))
    cmpr_lst = list(csv_yield_one_field(compare_file, 6, header= True))

    check_exist(cmpr_lst, base_lst)

if __name__ == "__main__":
    main()

