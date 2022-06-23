import sqlite3

conn = sqlite3.connect("test.db")
cursor = conn.cursor()

cursor.execute('''DROP TABLE IF EXISTS MESSAGES''')

conn.execute('''CREATE TABLE MESSAGES
         (MSG           TEXT    NOT NULL);''')

conn.close()
