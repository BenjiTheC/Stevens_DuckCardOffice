import sqlite3
import os


db = '/Users/benjamin/Documents/Campus_Card_Office/Stevens_DuckCardOffice/duckcard.db'
connection = sqlite3.connect(db)
cursor = connection.cursor()

query =\
    """ SELECT sla.cwid
        FROM Slate as sla 
    """

cursor.execute(query)
for row, in cursor:
    print(row)

connection.close()