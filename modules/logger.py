import sqlite3

def log_event(e):
    conn=sqlite3.connect("database.db")
    c=conn.cursor()
    c.execute("INSERT INTO logs(event) VALUES(?)",(e,))
    conn.commit()
    conn.close()

def fetch_logs():
    conn=sqlite3.connect("database.db")
    c=conn.cursor()
    data=c.execute("SELECT * FROM logs").fetchall()
    conn.close()
    return data