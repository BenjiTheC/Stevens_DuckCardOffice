""" 
3 files given
do 
newad - suspect - continuing
"""

from strcon import file_reading_gen

def to_del(suspect, continuing):
    """ extract the cwid"""
    to_delete = list()

    for cwid, first, middle, last in file_reading_gen(suspect, 4, header= True):
        to_delete.append(cwid)

    for cwid, first, middle, last in file_reading_gen(continuing, 4, header= True):
        to_delete.append(cwid)

    return to_delete

def write_new(newad, to_del: list):
    """ delete the sus and con, write into a new file"""
    with open('Brand_new_1108.csv', 'x') as towrite:

        uggr = 'GR'
        exitdate = '12/31/2022'
        towrite.write("CWID,First,Middle,Last,UG/GR,ExitDate\n")
        counter = 0
        sub = 0

        for cwid, first, middle, last, username, email, dcisionfn, pround, defer, dcisionln, pchange, special in file_reading_gen(newad, 12, header= True):
            counter += 1
            
            if cwid in to_del:
                print(f"Skipping student {cwid},{first},{middle},{last}")              
                sub += 1
                continue
                
            towrite.write(f"{cwid},{first},{middle},{last},{uggr},{exitdate}\n")

        else:
            print(f"\t{counter} students read from newad")
            print(f"\t{sub} students skipped")
            print(f"\t{counter - sub} students written into the new file")


def main():
    newad = "/Users/benjamin/Documents/Campus_Card_Office/photo_upload/Newad_1108.csv"
    sus = "/Users/benjamin/Documents/Campus_Card_Office/photo_upload/SUSPECT_1108.csv"
    con = "/Users/benjamin/Documents/Campus_Card_Office/photo_upload/Continuing_1108.csv"
    
    todel = to_del(sus, con)
    print(f"Number to delete checking: {len(todel)}")
    write_new(newad, todel)

if __name__ == "__main__":
    main()