import sqlite3
import os
from contextlib import contextmanager

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATABASE_PATH = os.path.join(BASE_DIR, "mydatabase.db")
# DATABASE_PATH = "mydatabase.db"  # 你生成的 SQLite 文件路径

@contextmanager
def get_db():
    """
    获取 SQLite 数据库连接并开启外键支持
    用法：
        with get_db() as (conn, cursor):
            cursor.execute(...)
    """
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row  # 查询结果可按列名访问
    conn.execute("PRAGMA foreign_keys = ON;")
    cursor = conn.cursor()

    try:
        yield conn, cursor
        conn.commit()
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()



'''
from database import get_db

with get_db() as (conn, cursor):
    cursor.execute("SELECT * FROM tags")
    rows = cursor.fetchall()
    for row in rows:
        print(row["name"])

'''