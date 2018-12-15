""" 
Everyday we will receive a .csv file of the report of how many photos we 
have approved/rejected/pending. 
build a database to check and update the data of every individual's photo
"""

import os
import sqlite3
from datetime import datetime
from read_file import file_reading_gen

curdir = os.path.abspath(os.path.dirname(__file__))

class CheckApprove:
    """ 
    Dawn will send photo upload report to me everyday, and I need to update
    the record that how many approved photo has been printed and how many have not
    By building the reference, which I will only build it once. I will check the 
    incoming file each and every day to see if there are any new approved photos 
    that have not been printed out.

    - build ref: only excute once --> very first time this scrpit is running
    - the database will have following attributes:
      - cwid
      - first
      - middle
      - last
      - status:     --> approved, pending, rejected
      - operation date: date received the file
    """

    def __init__(self, date, db_file='/Users/benjamin/Documents/Campus_Card_Office/DuckCard_data/photoAdmin/photo_admin.db'):
        """
        - build reference at the first time we run it
        - check and update data every time we has a file

        - pull out the data as a file
          - only approved record
          - only ones we approved at [date]

        - date: 4 digit string
        """
        self._date = date                    # date received the file
        self._db_file = db_file

        self._build_ref()

        self._update_ref()

    @staticmethod
    def status(status_string: str):
        """return the status from the long string"""
        status_tup = ('approved', 'pending', 'rejected')
        for status in status_tup:
            if status in status_string:
                return status

    def _build_ref(self):
        """ 
        This example is extremly opposite to definition of extensive program
        I assume myself already know where the file is and what to build
        """
        connection = sqlite3.connect(self._db_file)
        ref = connection.cursor()

        # build the table as prime reference
        Query_tbl = \
        """
        CREATE TABLE IF NOT EXISTS reference
        (
            CWID TEXT,
            First TEXT,
            Last TEXT,
            Status TEXT,
            SubmitDate TEXT,
            Date TEXT
        )
        """
        ref.execute(Query_tbl)

        connection.commit()
        connection.close()

    def _update_ref(self):
        """ 
        we only manipulate one table
        for every cwid in the new file:
            - if it's in the database?
                - YES: if their status are the same?
                    - YES: do nothing
                    - NO : update the *status* and *date*
                - NO : add them in the database
        """

        connection = sqlite3.connect(self._db_file) 
        update = connection.cursor()

        Query_sle = \
        """
        SELECT ref.CWID, ref.First, ref.Last, ref.Status, ref.SubmitDate, ref.Date
        FROM reference AS ref
        WHERE ref.CWID = ?
        """

        Query_ins = \
        """
        INSERT INTO reference (CWID, First, Last, Status, SubmitDate, Date)
        VALUES (?, ?, ?, ?, ?, ?);
        """

        Query_upd = \
        """
        UPDATE reference 
        SET Status = ?, SubmitDate = ?, Date = ?
        WHERE CWID = ?
        """

        for cwid, first, last, status, submitdate, email, uggr \
            in file_reading_gen(f'/Users/benjamin/Documents/Campus_Card_Office/DuckCard_data/photoAdmin/receivedJSA/photo_upload_admin_{self._date}.csv', 7):
            
            try:
                record = list(update.execute(Query_sle, (cwid, )))[0]          # Cursor is a generator object, not a list.
            except IndexError:
                record = list(update.execute(Query_sle, (cwid, )))
            # record = [cwid, first, last, status, submitdate, operation_date]
            
            status = self.status(status)

            # new record
            if not record:
                
                data = (cwid, first, last, status, submitdate, self._date)
                update.execute(Query_ins, data)

            # existed record but has a status change
            # format of SubmitDate: mm/dd/yy hh:mm --> %m/%d/%y %H:%M
            elif record and status != record[3] \
                and datetime.strptime(record[4], '%Y-%m-%d %H:%M:%S') <= datetime.strptime(submitdate, '%Y-%m-%d %H:%M:%S'): 
                
                data = (status, submitdate, self._date, cwid)
                update.execute(Query_upd, data)

            elif record and status == record[3]:
                pass

            connection.commit()

        connection.close()

    def write_file(self, wanted_status='approved'):
        """
        - pull out the data from database
        - only approved photos' data
        - only approved photos at [date]
        """
        
        connection = sqlite3.connect(self._db_file)
        pull = connection.cursor()

        Query_sle = \
        """
        SELECT ref.CWID, ref.First, ref.Last, ref.Date
        FROM reference AS ref
        WHERE ref.Status = ? and ref.Date = ?
        """
        data = (wanted_status, self._date)
        
        if list(pull.execute(Query_sle, data)):
            with open(f'/Users/benjamin/Documents/Campus_Card_Office/DuckCard_data/photoAdmin/toPrint/approved_{self._date}.csv', 'w') as fwrite:
                fwrite.write('CWID,First,Last,Date\n')


                for cwid, first, last, date in pull.execute(Query_sle, data):
                    fwrite.write(f'{cwid},{first},{last},{date}\n')

                print('writing finish.')

def main():
    """ Entrance"""
    CheckApprove('1212').write_file()
    

if __name__ == "__main__":
    main()
