import sqlite3

# Teste para inserir na bd um objeto detetado

conn = sqlite3.connect("test.db")
cursor = conn.cursor()

cursor.execute('''INSERT INTO MESSAGES VALUES (?)''', ["Cão"])

conn.commit()
