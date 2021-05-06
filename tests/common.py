from enum import Enum

from pyodbc import Connection, Cursor

reference_data = [(1, "User1"), (2, "User2"), (3, "User3"), (4, "User4"), (5, "User5")]


class InsertStrategy(Enum):
    SEQUENTIAL = 1
    EXECUTEMANY = 2
    EXECUTEMANY_FAST = 3


def insert_data(
    conn: Connection,
    strategy: InsertStrategy = InsertStrategy.SEQUENTIAL,
    refresh_table=False,
):

    cursor: Cursor = conn.cursor()

    # Recreate table.
    cursor.execute("DROP TABLE IF EXISTS users;")
    cursor.execute('CREATE TABLE users ("id" BIGINT, "name" VARCHAR(255));')

    # Insert data.
    sql = f"INSERT INTO users (id, name) VALUES (?, ?);"
    if strategy == InsertStrategy.SEQUENTIAL:
        for record in reference_data:
            cursor.execute(sql, record)
    elif strategy == InsertStrategy.EXECUTEMANY:
        cursor.executemany(sql, reference_data)
    elif strategy == InsertStrategy.EXECUTEMANY_FAST:
        cursor.fast_executemany = True
        cursor.executemany(sql, reference_data)
    cursor.commit()
    cursor.close()

    # Synchronize write.
    if refresh_table:
        conn.execute("REFRESH TABLE users;")


def select_data(conn: Connection):

    cursor: Cursor = conn.cursor()
    cursor.execute("SELECT * FROM users ORDER BY id;")
    result = cursor.fetchall()
    cursor.close()
    result = list(map(tuple, result))
    return result
