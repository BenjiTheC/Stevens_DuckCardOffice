"""
INPUT: .csv file 
OUTPUT: join all the name

"""

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

def campus_lib(filepath):
    """ write a big data file"""
    with open('campus.csv', 'x') as fwrite:

        fwrite.write(f"CWID,First,Middle,Last,UG/GR,ExitDate\n")

        for cwid, first, middle, last, uggr, exp in file_reading_gen(filepath, 6, header= True):
            
            first = first.strip().split(' ')[0] 
                            
                
            fwrite.write(f"{cwid},{first.upper()},{middle.upper()},{last.upper()},{uggr},{exp}\n")

def newad(filepath):
    """ newly admit stu"""
    with open('New_Admitted_1106-08.csv', 'x') as fwrite:

        fwrite.write(f"CWID,First,Middle,Last,UserID,Email,Decision First Name,Round,Defer to Term,Decision Last Name,Is this a program change?,Special Program\n")

        for cwid, first, middle, last, username, email, dcisionfn, pround, defer, dcisionln, pchange, special in file_reading_gen(filepath, 12, header= True):
            
            first = first.strip().split(' ')[0]

            fwrite.write(f"{cwid},{first.upper()},{middle.upper()},{last.upper()},{username},{email},{dcisionfn},{pround},{defer},{dcisionln},{pchange},{special}\n")


def main():
    dataset_path = "/Users/benjamin/Documents/Campus_Card_Office/photo_upload/InCampusPersonnel.csv"
    newad_path = "/Users/benjamin/Documents/Campus_Card_Office/photo_upload/Export_1106-08.csv"
    campus_lib(dataset_path)
    newad(newad_path)

if __name__ == "__main__":
    main()
