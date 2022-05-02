###########################################################################
Troubleshooting CrateDB with Progress DataDirect ODBC Driver for PostgreSQL
###########################################################################


**The issue documented in this repository was resolved in Progress DataDirect ODBC for PostgreSQL version 08.02.0795.**

************
Introduction
************

This is an interesting ODBC/Python-related issue when using the
`Progress DataDirect PostgreSQL ODBC Driver`_ to insert data using ``pyodbc``
into CrateDB_.


**************
Problem report
**************

When enabling ``pyodbc``'s ``fast_executemany`` setting, parameterized
``INSERT`` statements won't insert more than two rows. Without that setting,
all rows get inserted as expected.

The documentation for that setting says:

    This read/write attribute specifies whether to use a faster
    ``executemany()`` which uses parameter arrays.

Running the same against vanilla PostgreSQL works fine. When using PostgreSQL's
official ODBC driver, `psqlODBC - PostgreSQL ODBC driver`_, the problem does
not happen with CrateDB.

Did we ever encounter a similar problem with other drivers? A complete Python
script to reproduce is available within ``attic/minimal-repro.py``.


************
Reproduction
************

Derived from ``minimal-repro.py``, there is now a test suite which fully covers
the whole scenario with different cases. It invokes the test suite on both
databases (PostgreSQL vs. CrateDB), using both driver variants (psqlODBC vs.
DataDirect PostgreSQL ODBC), with three variants of inserts (sequential,
executemany, fast_executemany).

The test suite includes all ODBC driver files needed for running it on Linux
without further ado. Only unixODBC is needed.

Install prerequisites::

    # Debian and Ubuntu
    apt-get install --yes unixodbc-dev

    # macOS
    brew install unixodbc

Run PostgreSQL and CrateDB side by side::

    # Run PostgreSQL 13 and create database
    docker run -it --rm --env "POSTGRES_HOST_AUTH_METHOD=trust" --publish=5432:5432 --name postgresql postgres:13.2
    psql postgres://postgres@localhost --command "CREATE DATABASE doc;"

    # Run CrateDB
    docker run -it --rm --publish=4200:4200 --publish=6432:5432 crate/crate:4.5.1

Invoke testsuite on workstation::

    export LD_LIBRARY_PATH=$PWD/drivers/linux
    make test

Invoke testsuite on Docker (needed when not running Linux)::

    docker run -it --rm --network=host --volume=$PWD:/src python:3.9 bash
    apt-get update && apt-get install --yes unixodbc-dev
    cd /src
    export LD_LIBRARY_PATH=/src/drivers/linux
    make test


************
Observations
************

Test suite
==========

Indeed, when using the ``fast_executemany`` option with the *Progress
DataDirect PostgreSQL ODBC Driver*, it is **occasionally** failing the test.

All other variants covered by the testsuite always succeed. The
``fast_executemany`` option apparently also does no harm when using the
*psqlODBC - PostgreSQL ODBC driver*.

In order to specifically run those tests, invoke::

    make test-trouble

Test suite report fragment for ``fast_executemany @ ddpsql @ cratedb``::

    tests/test_ddpsql.py::test_ddpsql_cratedb_executemany_fast[InsertStrategy.EXECUTEMANY_FAST-0] PASSED
    tests/test_ddpsql.py::test_ddpsql_cratedb_executemany_fast[InsertStrategy.EXECUTEMANY_FAST-1] PASSED
    tests/test_ddpsql.py::test_ddpsql_cratedb_executemany_fast[InsertStrategy.EXECUTEMANY_FAST-2] PASSED
    tests/test_ddpsql.py::test_ddpsql_cratedb_executemany_fast[InsertStrategy.EXECUTEMANY_FAST-3] FAILED
    tests/test_ddpsql.py::test_ddpsql_cratedb_executemany_fast[InsertStrategy.EXECUTEMANY_FAST-4] PASSED
    tests/test_ddpsql.py::test_ddpsql_cratedb_executemany_fast[InsertStrategy.EXECUTEMANY_FAST-5] FAILED
    tests/test_ddpsql.py::test_ddpsql_cratedb_executemany_fast[InsertStrategy.EXECUTEMANY_FAST-6] PASSED
    tests/test_ddpsql.py::test_ddpsql_cratedb_executemany_fast[InsertStrategy.EXECUTEMANY_FAST-7] PASSED
    tests/test_ddpsql.py::test_ddpsql_cratedb_executemany_fast[InsertStrategy.EXECUTEMANY_FAST-8] PASSED
    tests/test_ddpsql.py::test_ddpsql_cratedb_executemany_fast[InsertStrategy.EXECUTEMANY_FAST-9] FAILED

The failed tests mostly demonstrate that the queried data is empty::

    >       assert result == reference_data
    E       AssertionError: assert left == right failed.
    E         Showing unified diff (L=left, R=right):
    E
    E          L []
    E          R [(1, 'User1'), (2, 'User2'), (3, 'User3'), (4, 'User4'), (5, 'User5')]

However, sometimes there is an anomaly like::

    >       assert result == reference_data
    E       AssertionError: assert left == right failed.
    E         Showing unified diff (L=left, R=right):
    E
    E          L [(2, 'User2')]
    E          R [(1, 'User1'), (2, 'User2'), (3, 'User3'), (4, 'User4'), (5, 'User5')]

Occasionally, this exception can be observed::

    conn = <pyodbc.Connection object at 0x7f030955c8f0>

        def select_data(conn: Connection):

            cursor: Cursor = conn.cursor()
            cursor.execute("SELECT * FROM users ORDER BY id;")
    >       result = cursor.fetchall()
    E       pyodbc.ProgrammingError: No results.  Previous SQL was not a query.


Trace logs
==========

Apply
-----

In order to enable corresponding tracing options, invoke those SQL statements::

    SET GLOBAL 'logger.io.crate.action.sql' = 'TRACE';
    SET GLOBAL 'logger.io.crate.protocols.postgres' = 'TRACE';

Apply them using either Admin UI, crash, or psql, like::

    psql postgres://crate@localhost:6432 --command "SET GLOBAL 'logger.io.crate.action.sql' = 'TRACE';"
    psql postgres://crate@localhost:6432 --command "SET GLOBAL 'logger.io.crate.protocols.postgres' = 'TRACE';"

Then, run the offending database workload, like::

    pytest -k "cratedb and ddpsql and many and fast" -vvv

Evaluate
--------

In order to get meaningful insights into the log files, the ``./reports``
folder contains trace logs of particular spots of the test suite as well
as corresponding comparison reports in form of diff files.

To produce those, the database workload has been invoked using both
``executemany`` vs. the ``fast_executemany`` strategies on each driver,
``ddpsql`` vs. ``psqlodbc``.

The results from those comparisons have been sanitized, diffed and stored at:

- ``./reports/01-trace/ddpsql.diff``
- ``./reports/01-trace/psqlodbc.diff``


.. _CrateDB: https://github.com/crate/crate
.. _Progress DataDirect PostgreSQL ODBC Driver: https://www.progress.com/odbc/postgresql
.. _psqlODBC - PostgreSQL ODBC driver: https://odbc.postgresql.org/
