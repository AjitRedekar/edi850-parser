from pathlib import Path

import pytest

from edi850 import parse_850
from validate import validate_order

DATA = Path(__file__).parent / "data"


@pytest.mark.parametrize(
    "file_name, expected_problems",
    [
        ("sample.850", ["Line 3: quantity is 0"]),
        (
            "bad.850",
            [
                "Line 3: quantity is 0",
                "declared line count 3 not matching with number of lines 2 processed",
            ],
        ),
        (
            "empty_n1.850",
            ["Missing ship-to name", "Missing ship-to city", "Line 3: quantity is 0"],
        ),
    ],
)
def test_problems_detected(file_name, expected_problems):
    order = parse_850(DATA / file_name)
    problems = validate_order(order)
    assert [problem for problem in problems] == expected_problems


def test_problem_for_good_data():
    order = parse_850(DATA / "sample.850")
    order.lines[2].qty = 1
    problems = validate_order(order)
    assert len(problems) == 0
