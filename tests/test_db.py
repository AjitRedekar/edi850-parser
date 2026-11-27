from pathlib import Path

import pytest
import sqlite3

from edi850 import parse_850
from db import load_order

DATA = Path(__file__).parent / "data"


def test_getOrder():
    order = parse_850(DATA / "good.850")
    conn = sqlite3.Connection("orders.db")
    assert load_order(conn, order.guid) == order
