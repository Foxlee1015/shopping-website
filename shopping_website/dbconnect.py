from flask_mysqldb import MySQLdb

def connection():
    conn = MySQLdb.connect(host="localhost",
                           user="root",
                           passwd="50174397",
                           db="users",
                           )
    c = conn.cursor()
    return c, conn
