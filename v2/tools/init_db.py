import sqlite3

with open ("./tools/init.sql", "r", encoding="utf-8") as f:
    sql = f.read()

conn = sqlite3.connect("./data/mobypark.db")
conn.executescript(sql)
conn.commit()
conn.close()

print("Database initialized.")