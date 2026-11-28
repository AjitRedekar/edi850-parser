import sqlite3
from pathlib import Path

import pytest

from db import init_db, load_order, save_order, order_summary
from edi850 import parse_850
from models import Order

DATA = Path(__file__).parent / "data"


@pytest.fixture
def conn():
    """A fresh, empty in-memory database for each test."""
    connection = sqlite3.connect(":memory:")
    init_db(connection)
    yield connection
    connection.close()


def test_save_and_load_round_trip(conn):
    order = parse_850(DATA / "good.850")
    save_order(conn, order)
    assert load_order(conn, order.guid) == order


def test_load_unknown_guid_returns_none(conn):
    assert load_order(conn, "no-such-guid") is None


def test_duplicate_PO_error_raise(conn):
    with pytest.raises(sqlite3.IntegrityError):
        order = parse_850(DATA / "good.850")
        save_order(conn, order)
        save_order(conn, order)


def test_order_summary(conn):
    for each_summary in order_summary(conn):
        order = load_order(conn, each_summary[0])
        assert each_summary[1] == order.po_number
        assert each_summary[2] == order.declared_line_count
