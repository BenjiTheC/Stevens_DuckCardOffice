""" Find the people who are in the Blackboard but haven't submit their photo"""

import os
import re
from read_file import file_reading_gen

def ref_lst(file_path):
    """ get the list of people's CWID who hasn't submitted their photo"""
    r_lst = list()
    for cwid in file_reading_gen(file_path, 1):
        s = cwid[0]
        re_obj = re.search(r'([\d]*)', s)
        r_lst.append(re_obj.group(1))

    return tuple(r_lst)

def write_file(r_lst, dir_path=os.path.abspath(os.path.dirname(os.curdir)), pattern=r'^Export_([\d]{4})$'):
    """ dirpath as os.curdir, write a file"""

    with open('photo_admin/mailmerge_list.csv', 'w') as fwrite:
        fwrite.write('CWID,First,Middle,Last,username,E-mail\n')

        # n: number of people who haven't submitted their photos
        n = 0
        for name in os.listdir(dir_path):

            if re.search(pattern, name) and os.path.isdir(name):            # find the Export_[exportDate] dir
                
                # open the file and find the info needed
                for cwid, first, middle, last, username, email, dcisionfn, prnd, defer, dcisionln, pchange, special \
                    in file_reading_gen(os.path.join(os.curdir, name, name + '.csv'), 12, header= True):
                    
                    if cwid in r_lst:         # hasn't uploaded the photo
                        print(f'writing {cwid}, {first}, {middle}, {last}, {email}')
                        fwrite.write(f'{cwid},{first},{middle},{last},{username},{email}\n')

                        n += 1

        print(f'writing finished, {n} in total written into the file')

def main():
    """ Entrance"""
    filepath = '/Users/benjamin/Documents/Campus_Card_Office/Stevens_DuckCardOffice/NOT_SUBMIT_PHOTO.csv'
    lst = ref_lst(filepath)
    write_file(lst)

if __name__ == '__main__':
    main()
