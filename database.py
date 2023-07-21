from flask import g
import sqlite3
import os

database_path = os.getenv("DATABASE_PATH")

# Database helpers
def connect_db():
    sql = sqlite3.connect(database_path)
    sql.row_factory = sqlite3.Row
    return sql


def get_db():
    if not hasattr(g, 'sqlite_db'):
        connect_db()
    return g.sqlite_db

