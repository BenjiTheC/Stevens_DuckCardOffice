""" a tool kit for file management"""

# File reading generator
def file_reading_gen(path, fields, sep=',', header=False):
    """ A generator that reads text files and returns all of the values on a single line on each call to next()"""
    try:
        open_file = open(path, 'r')
    except FileNotFoundError:
        raise FileNotFoundError(f"{path} can't be found or opened")
    else:
        with open_file:

            for ind, line in enumerate(open_file):
                if header:
                    header = False
                    continue

                res = line.rstrip('\n\r').split(sep)

                if len(res) != fields:               # raise ValueError if the fields don't match
                    raise ValueError(f"{path} has {len(res)} fields in line {ind} but expected {fields}")

                yield tuple(res)

def separate_line(line, sep=','):
    """ 
    separate the line with sep and don't include sep in the double-quotes(e.g "o,o") 
    return a list of tokens
    """
    line = line.rstrip('\n\r') + sep
    res = list()
    quote = 0
    word = list()

    for c in line:
        if c == '"' and quote == 0:         # start of a token
            quote = 1
        elif c == '"' and quote == 1:       # end of a token
            quote = 0
        elif c == sep and quote != 1:       # sep not in the token
            res.append("".join(word))
            word = list()
        else:
            word.append(c)                  # not a sep, not a quote
    
    return res

def nonpy_file_reading_gen(path, fields, sep=',', header=False):
    """ A generator that reads text files and returns all of the values on a single line on each call to next()"""
    try:
        open_file = open(path, 'r')
    except FileNotFoundError:
        raise FileNotFoundError(f"{path} can't be found or opened")
    else:
        with open_file:

            for ind, line in enumerate(open_file):
                if header:
                    header = False
                    continue
                
                res = separate_line(line, sep)

                if len(res) != fields:               # raise ValueError if the fields don't match
                    raise ValueError(f"{path} has {len(res)} fields in line {ind} but expected {fields}")

                yield tuple(res)

def get_one_column(file_path, fields, col, sep=',', header=True):
    """ Only get one specific column in a .csv file, col starts from 0.""" 
    if fields <= col:
        raise IndexError(f'The file {file_path} only has {fields} fields but you are asking for {col + 1}th column!')

    res = list()
    for row in file_reading_gen(file_path, fields, sep, header):
        res.append(row[col])

    return res

def main():
    """ Entrance"""
    #test_path = '/Users/benjamin/Documents/Campus_Card_Office/DuckCard_data/receivedExcel/Employee_list_for_Card_Office_review_20180727.csv'

    #for row in nonpy_file_reading_gen(test_path, 19, header=True):
    #    print(row[:5])

if __name__ == "__main__":
    main()
    