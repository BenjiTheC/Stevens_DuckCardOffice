""" For recording the issuing of the protective cases."""

import os
from datetime import datetime
from read_file import get_one_column

def get_issued(filepath):
    """ get the record of all personnel who received protective case before.
        return the value in a tuple
        fields is the number of fields each line in the filepath
    """
    return [] if not os.path.isfile(filepath) else tuple(get_one_column(filepath, 2, 0, header=True)) 

def is_issued(ref: tuple, target: str):
    """ Return True if the target has already been given a protective case."""
    return target in ref

def write_file(filepath, cwid):
    """ write the cwid into the file if it's not in the file"""
    first_time = not os.path.isfile(filepath)
    with open(filepath, 'a') as fwrite:
        if first_time:
            fwrite.write('CWID,issued time\n')
        
        issued_time = datetime.today().strftime('%Y-%m-%d %H:%M')
        fwrite.write(f'{cwid},{issued_time}\n')

def entrance(fp = os.path.join(os.curdir, 'test_issued_case.csv')):
    """ Entrance"""
    while True:
        print("\nInput Q/q to quit the program.")
        cwid = input('Please swipe the CWID:\t')

        if cwid in 'Qq':
            break

        if is_issued(get_issued(fp), cwid):
            print('This student is given a protective case already!!')
        else:
            print('Give him/her a protective case, s/he is a new one.')
            write_file(fp, cwid)

    print('Thank you for using, see you next time!')

if __name__ == '__main__':
    # entrance()
    pass
