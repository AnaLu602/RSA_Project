import sqlite3

conn = sqlite3.connect("test.db")

conn.execute('''DROP TABLE IF EXISTS CAMS''')
conn.execute('''DROP TABLE IF EXISTS DENMS''')

conn.execute('''CREATE TABLE CAMS
         (ID            INTEGER PRIMARY KEY,
         NAME           TEXT    NOT NULL,
         TIMESTAMP      INT     NOT NULL,
         LAT            REAL    NOT NULL,
         LONG           REAL    NOT NULL);''')

conn.execute('''CREATE TABLE DENMS
         (ID            INTEGER PRIMARY KEY,
         CAUSE          INT     NOT NULL,
         SUBCAUSE       INT     NOT NULL,
         TIMESTAMP      INT     NOT NULL,
         LAT            REAL    NOT NULL,
         LONG           REAL    NOT NULL);''')

conn.close()
