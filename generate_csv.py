""" Generate a csv file with login attempt"""


def readfile(filepath):
    
    with open(filepath, 'r') as openfile:

        info_dct = dict()       # key: cwid, value: username
        cwid = ''
        username = ''


        for line in openfile:
            if line.startswith('Login'):
                username = line.strip().split(' ')[1]

            if line.startswith('ID'):
                cwid = line.strip().split(' ')[2]

            if cwid and cwid not in info_dct:
                info_dct[cwid] = username
                cwid, username = '', ''

        print(f'printing info of file, {len(info_dct)} in total.\n')
        for cwid, username in info_dct.items():
            print(f'{cwid}: {username}')

        return info_dct

def writefile(info_dct: dict):
    
    with open('login_try.csv', 'w') as fwrite:

        fwrite.write(f'cwid,username\n')
        for cwid, username in info_dct.items():
            print(f'writing: {cwid},{username}')
            fwrite.write(f'{cwid},{username}\n')

        else:
            print('writing finish')

def main():
    filepath = '/Users/benjamin/Documents/Campus_Card_Office/Stevens_DuckCardOffice/login_attempt.txt'
    info_dct = readfile(filepath)
    writefile(info_dct)

if __name__ == '__main__':
    main()