from decimal import Decimal
import json
from datetime import datetime

EDI850_order_header_map = {
    ("BEG", 2, "str"): ("po_number",),
    ("BEG", 4, "date"): ("po_date",),
    ("N1", 1, "str"): (
        "ship_to",
        "name",
    ),
    ("N3", 0, "str"): (
        "ship_to",
        "address",
    ),
    ("N4", 0, "str"): (
        "ship_to",
        "city",
    ),
    ("N4", 1, "str"): (
        "ship_to",
        "state",
    ),
    ("N4", 2, "str"): (
        "ship_to",
        "zip",
    ),
}

EDI850_order_detail_map = {
    ("PO1", 0, "int"): ("line_no",),
    ("PO1", 1, "int"): ("qty",),
    ("PO1", 2, "str"): ("uom",),
    ("PO1", 3, "Deci"): ("price",),
    ("PO1", 6, "str"): ("item",),
    ("PID", 4, "str"): ("description",),
}


def parse_segment(line):
    """Return (segment_id, elements) for an EDI line, or (None, None) if blank."""
    line = line.strip().rstrip("~")
    if not line:
        return None, None
    elements = line.split("*")
    return elements[0], elements[1:]


def print_po_lines(po_lines):
    """Print PO1 details as an aligned table."""
    print(f"{'Line':>4} {'Qty':>5} {'UOM':<4} {'Price':>8} {'Cost':>10}")
    for po_line in po_lines:
        print(
            f"{po_line.get('line_no'):>4} {po_line.get('qty'):>5} {po_line.get('uom'):<4} {po_line.get('price'):>8.2f} {po_line.get('qty') * po_line.get('price'):>10.2f}"
        )  # total price


po_header = []
po_lines = []
order = {"po_number": None, "po_date": None, "ship_to": {}, "lines": []}

this_line = {
    "line_no": None,
    "qty": None,
    "uom": None,
    "price": Decimal(0),
    "item": None,
    "description": None,
}
po_lines2 = []

try:
    f = open("d:/GetAI/sample.850")
except FileNotFoundError as e1:
    print(f"File Access Error: {e1}")
    raise SystemExit(1)  # Exit the program if the file is not found

with f:
    for file_line_number, line in enumerate(f, start=1):

        segment_id, segment_elements = parse_segment(line)
        if segment_id is None:
            continue

        for (segment, position, el_type), element in EDI850_order_header_map.items():
            if segment_id == segment:
                if len(element) == 1:
                    try:
                        if el_type == "date":
                            order[element[0]] = datetime.strptime(
                                segment_elements[position], "%Y%m%d"
                            ).date()  # convert to date object

                        else:
                            order[element[0]] = segment_elements[position]
                    except ValueError as e:
                        print(f"Line {file_line_number}: skipped {segment_id} ({e})")
                else:
                    order[element[0]][element[1]] = segment_elements[position]

        for (segment, position, el_type), element in EDI850_order_detail_map.items():
            if segment_id == segment:
                if len(element) == 1:
                    try:
                        if el_type == "int":
                            this_line[element[0]] = int(segment_elements[position])
                        elif el_type == "Deci":
                            this_line[element[0]] = Decimal(segment_elements[position])
                        else:
                            this_line[element[0]] = segment_elements[position]

                    except ValueError as e:
                        print(f"Line {file_line_number}: skipped PO1 ({e})")

                    if segment == "PID" and this_line.get("description") is not None:
                        po_lines2.append(this_line)
                        this_line = {}  # Reset line for the next iteration

order["lines"] = po_lines2
with open("d:/GetAI/order.json", "w") as out:
    json.dump(order, out, indent=2, default=str)
