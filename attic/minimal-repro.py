"""
Minimal code example to reproduce flaw with Progress DataDirect ODBC Driver for PostgreSQL.

Setup on Ubuntu::

    apt-get install unixodbc odbc-postgresql

For DataDirect:
1) Download the driver from https://www.progress.com/odbc/postgresql
2) apt-get install ksh
3) sudo ./unixmi.ksh
4) source /opt/Progress/DataDirect/Connect64_for_ODBC_71/odbc.sh && python3 test_minimal.py
"""
import pyodbc


def main():

    # DataDirect with CrateDB
    conn = pyodbc.connect('DRIVER=/opt/Progress/DataDirect/Connect64_for_ODBC_71/lib/ddpsql27.so;HOST=presales.bregenz.a1.cratedb.net;PORT=5432;UID=niklas;PWD=***;DB=doc;EncryptionMethod=1;ValidateServerCertificate=0')

    # PostgreSQL with CrateDB
    #conn = pyodbc.connect('Driver={PostgreSQL Unicode};Server=presales.bregenz.a1.cratedb.net;Port=5432;Database=doc;Uid=niklas;Pwd=***;sslmode=require')

    # DataDirect with PostgreSQL
    #conn = pyodbc.connect('DRIVER=/opt/Progress/DataDirect/Connect64_for_ODBC_71/lib/ddpsql27.so;HOST=localhost;PORT=5432;UID=postgres;PWD=postgres;DB=odbc_test')

    cursor = conn.cursor()

    cursor.execute('DROP TABLE IF EXISTS doc.users;')
    cursor.execute('CREATE TABLE doc.users("id" BIGINT, "name" VARCHAR(255));')

    # if fast_executemany == True && DataDirect with CrateDB: issue is reproducible
    # else: issue does not occur
    cursor.fast_executemany = True
    sql = f"INSERT INTO doc.users (id, name) VALUES (?, ?);"
    cursor.executemany(sql, [(1, 'User1'), (2, 'User2'), (3, 'User3'), (4, 'User4'), (5, 'User5')])

    cursor.commit()


if __name__ == "__main__":
    main()
