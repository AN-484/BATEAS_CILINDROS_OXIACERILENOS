import sqlite3
conn = sqlite3.connect('db.sqlite3')
cursor = conn.cursor()
# Listar tablas
cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
print(cursor.fetchall())
# Consultar datos
cursor.execute("SELECT * FROM estado_cilindros")
print(cursor.fetchall())
conn.close()