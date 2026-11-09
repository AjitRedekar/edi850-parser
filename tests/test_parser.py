from pathlib import Path
from decimal import Decimal

import pytest

from edi850 import parse_850
from models import OrderLine

DATA = Path(__file__).parent / "data"


def test_header_fields():
    order = parse_850(DATA / "sample.850")
    assert order.po_number == "4500123456"
    assert order.ship_to.city == "COLUMBUS"


def test_bill_to_does_not_overwrite_ship_to():
    order = parse_850(DATA / "bill_to.850")
    assert order.ship_to.name == "ACME RETAIL DC 7"
    assert order.ship_to.city == "COLUMBUS"


def test_short_N4_gets_city():
    order = parse_850(DATA / "short_n4.850")
    assert order.ship_to.city == "COLUMBUS"
    assert order.ship_to.state is None
    assert order.ship_to.zip is None


def test_not_850_returns_none():
    assert parse_850(DATA / "not_850.850") is None


def test_missing_file_raises():
    with pytest.raises(FileNotFoundError):
        parse_850(DATA / "does_not_exist.850")


def test_extended_value():
    line = OrderLine(line_no=1, qty=24, uom="EA", price=Decimal("12.50"))
    assert line.extended_value() == Decimal("300.00")


@pytest.mark.parametrize(
    "file_name, expected_lines",
    [
        ("sample.850", [1, 2, 3]),
        ("bad.850", [1, 3]),
        ("bill_to.850", [1, 2, 3]),
        ("early_pid.850", [2, 3]),
        ("short_po1.850", [1, 2]),
        ("short_n4.850", [1, 2, 3]),
        ("empty_n1.850", [1, 2, 3]),
        ("no_pid.850", [1, 2, 3]),
        ("bad_price.850", [2, 3]),
    ],
)
def test_line_numbers(file_name, expected_lines):
    order = parse_850(DATA / file_name)
    assert [line.line_no for line in order.lines] == expected_lines
