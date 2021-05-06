import sys
from pathlib import Path

import pyodbc
import pytest
from pyodbc import Connection

from tests.common import InsertStrategy, insert_data, reference_data, select_data

driver = Path("drivers") / sys.platform / f"ddpsql27.so"


pytestmark = pytest.mark.skipif(
    sys.platform == "darwin", reason="DataDirect ODBC Driver not available for Darwin"
)


@pytest.mark.parametrize(
    "strategy",
    [
        InsertStrategy.SEQUENTIAL,
        InsertStrategy.EXECUTEMANY,
        InsertStrategy.EXECUTEMANY_FAST,
    ],
)
def test_ddpsql_postgresql(strategy):

    conn: Connection = pyodbc.connect(
        f"Driver={driver};Server=localhost;Port=5432;Database=doc;Uid=postgres"
    )

    insert_data(conn, strategy=strategy)

    result = select_data(conn)
    assert result == reference_data

    conn.close()


@pytest.mark.parametrize(
    "strategy", [InsertStrategy.SEQUENTIAL, InsertStrategy.EXECUTEMANY]
)
def test_ddpsql_cratedb(strategy):

    conn: Connection = pyodbc.connect(
        f"Driver={driver};Server=localhost;Port=6432;Database=doc;Uid=crate"
    )

    insert_data(conn, strategy=strategy, refresh_table=True)

    result = select_data(conn)
    assert result == reference_data

    conn.close()


@pytest.mark.parametrize("iteration", range(10))
@pytest.mark.parametrize("strategy", [InsertStrategy.EXECUTEMANY_FAST])
def test_ddpsql_cratedb_executemany_fast(iteration, strategy):

    conn: Connection = pyodbc.connect(
        f"Driver={driver};Server=localhost;Port=6432;Database=doc;Uid=crate"
    )

    insert_data(conn, strategy=strategy, refresh_table=True)

    result = select_data(conn)
    assert result == reference_data

    conn.close()
