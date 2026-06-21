import os

import psycopg2

DSN = os.environ.get("DATABASE_URL", "postgresql://dwh:dwh@localhost:5432/dwh")


def connect():
    conn = psycopg2.connect(DSN)
    conn.autocommit = True
    return conn


def execute(sql):
    conn = connect()
    try:
        with conn.cursor() as cur:
            cur.execute(sql)
    finally:
        conn.close()


def query(sql):
    conn = connect()
    try:
        with conn.cursor() as cur:
            cur.execute(sql)
            columns = [d[0] for d in cur.description]
            return columns, cur.fetchall()
    finally:
        conn.close()


def scalar(sql):
    _, rows = query(sql)
    return rows[0][0] if rows else None
