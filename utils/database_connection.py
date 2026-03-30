import sqlite3

def _connect_db():
    con = sqlite3.connect(database=r'ims.db')
    return con, con.cursor()