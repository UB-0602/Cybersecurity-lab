import sqlite3

conn = sqlite3.connect("database.db")
c = conn.cursor()

c.execute("""
CREATE TABLE users(
id INTEGER PRIMARY KEY AUTOINCREMENT,
username TEXT,
password TEXT,
role TEXT)
""")

c.execute("""
CREATE TABLE logs(
id INTEGER PRIMARY KEY AUTOINCREMENT,
event TEXT)
""")

# default admin
c.execute("INSERT INTO users VALUES (NULL,'admin','admin123','admin')")

conn.commit()
conn.close()
print("DB Ready")