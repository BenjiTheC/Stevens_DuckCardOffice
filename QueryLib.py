""" Store some frequently used SQL"""

#import os
#import sqlite3

class Query:
    """ Store some frequently used SQL"""
   # stevens_system.py
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
                raw_username TEXT,
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
            (cwid, first, middle, last, raw_first, raw_middle, raw_last, raw_email, raw_username, received_date)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
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

   # nerdy_ben.py
    # 1 field: Slate received_date
    find_con =\
        """ SELECT sla.cwid, sla.raw_first, sla.raw_middle, sla.raw_last
            FROM Slate as sla 
            JOIN Blackboard as bb
              ON sla.cwid = bb.cwid
            WHERE bb.received_date = '181111' 
              AND sla.received_date = ?;
        """

    # 1 field: Slate received_date
    find_sus =\
        """ SELECT DISTINCT sla.cwid, sla.raw_first, sla.raw_middle, sla.raw_last
            FROM Slate AS sla
            JOIN Blackboard AS bb
              ON sla.first = bb.first
              AND sla.last = bb.last 
              AND NOT (bb.middle != sla.middle and bb.middle != '' and sla.middle != '')
            WHERE sla.received_date = ?
              AND sla.cwid != bb.cwid
              AND sla.cwid NOT IN (
                SELECT sla.cwid
                FROM Slate sla
                JOIN Blackboard bb
                  ON sla.cwid = bb.cwid
                WHERE bb.received_date = '181111'
            );
        """
    
    # 3 fields: Slate received_date * 3
    find_brn =\
        """ SELECT DISTINCT cwid, raw_first, raw_middle, raw_last
            FROM Slate
            WHERE received_date = ?
            AND cwid NOT IN (

                SELECT DISTINCT sla.cwid
                FROM Slate AS sla
                JOIN Blackboard AS bb
                ON sla.first = bb.first
                AND sla.last = bb.last 
                AND NOT (bb.middle != sla.middle and bb.middle != '' and sla.middle != '')
                WHERE sla.received_date = ?
                AND sla.cwid != bb.cwid
                AND sla.cwid NOT IN (
                    SELECT sla.cwid
                    FROM Slate sla
                    JOIN Blackboard bb
                    ON sla.cwid = bb.cwid
                    WHERE bb.received_date = '181111'
                )

                UNION

                SELECT sla.cwid
                FROM Slate as sla 
                JOIN Blackboard as bb
                ON sla.cwid = bb.cwid
                WHERE bb.received_date = '181111' 
                AND sla.received_date = ?

            );
        """

    cwid_in_bb =\
        """ SELECT cwid
            FROM Blackboard
        """
    
    # TODO: below this line are not tested
    select_status_jsa =\
        """ SELECT jsa.cwid, jsa.first, jsa.last, jsa.received_date
        FROM JSA jsa
        WHERE jsa.received_date = ? 
          AND jsa.status = ?;
        """


def main():
    """ Test"""
    #query = Query()
    #connection = sqlite3.connect(':memory:')
    #cursor = connection.cursor()

    #cursor.execute(query.create_jsa)
    #connection.commit()
    #connection.close()

if __name__ == '__main__':
    main()
