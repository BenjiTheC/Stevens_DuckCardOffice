""" Store some frequently used SQL"""

#import os
import sqlite3

class Query:
    """ Store some frequently used SQL"""

    create_slate =\
        """ CREATE TABLE IF NOT EXISTS Slate
            (
                cwid TEXT,
                first TEXT,
                middle TEXT,
                last TEXT,
                raw_first TEXT,
                raw_middle TEXT,
                raw_last TEXT,
                raw_email TEXT,
                received_date TEXT
            );
        """

    create_bb =\
        """ CREATE TABLE IF NOT EXISTS Blackboard
            (
                cwid TEXT,
                first TEXT,
                middle TEXT,
                last TEXT,
                raw_first TEXT,
                raw_middle TEXT,
                raw_last TEXT,
                received_date TEXT
            );
        """
    
    create_jsa =\
        """ CREATE TABLE IF NOT EXISTS JSA
            (
                cwid TEXT,
                first TEXT,
                last TEXT,
                status TEXT,
                submit_date TEXT,
                received_date TEXT
            );
        """

    # 9 args fields
    insert_slate =\
        """ INSERT INTO Slate 
            (cwid, first, middle, last, raw_first, raw_middle, raw_last, raw_email, received_date)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """

    # 9 args fields
    insert_bb =\
        """ INSERT INTO Blackboard 
            (cwid, first, middle, last, raw_first, raw_middle, raw_last, received_date)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """

    # 6 args fields
    insert_jsa =\
        """ INSERT INTO JSA 
            (cwid, first, last, status, submit_date, received_date)
            VALUES (?, ?, ?, ?, ?, ?)
        """

    # 4 args fields
    update_jsa =\
        """ UPDATE JSA 
            SET status = ?, submit_date = ?, received_date = ?
            WHERE cwid = ?
        """

    update_bb =\
        """ UPDATE Blackboard 
            SET middle = '', raw_middle = ''
            WHERE raw_middle = '{null}';
        """

    select_existed_jsa =\
        """ SELECT cwid, first, last, status, submit_date, received_date
            FROM JSA
            WHERE cwid = ?
        """

    count_by_date_slate =\
        """ SELECT received_date, COUNT(*)
            FROM Slate
            GROUP BY received_date;
        """

    count_by_date_bb =\
        """ SELECT received_date, COUNT(*)
            FROM Blackboard
            GROUP BY received_date;
        """
    
    count_by_date_jsa =\
        """ SELECT received_date, COUNT(*)
            FROM JSA
            GROUP BY received_date;
        """

    get_indb_bb =\
        """ SELECT cwid FROM Blackboard
        """

def main():
    """ Test"""
    query = Query()
    connection = sqlite3.connect(':memory:')
    cursor = connection.cursor()

    cursor.execute(query.create_jsa)
    connection.commit()
    connection.close()

if __name__ == '__main__':
    main()
