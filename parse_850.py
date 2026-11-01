import sys
from decimal import Decimal, InvalidOperation
import json
from datetime import datetime
import uuid

EDI850_order_header_map = {
    ("BEG", 2, "str"): ("po_number",),
    ("BEG", 4, "date"): ("po_date",),
    ("N1", None, "after:ST"): (
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
    ("PO1", 3, "decimal"): ("price",),
    ("PO1", None, "after:VP"): ("item",),
    ("PID", 4, "str"): ("description",),
}

# po_lines = []
order = {"guid": None, "po_number": None, "po_date": None, "ship_to": {}, "lines": []}


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
    for line_count, po_line in enumerate(po_lines):
        if po_line == None:
            continue
        else:
            print(
                f"{po_line.get('line_no'):>4} {po_line.get('qty'):>5} {po_line.get('uom'):<4} {po_line.get('price'):>8.2f} {po_line.get('qty') * po_line.get('price'):>10.2f}"
            )  # total price


def map_order_header(segment_id, segment_elements, file_line_number):

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
                if el_type.startswith("after:"):
                    qualifier = el_type.split(":")[1]
                    order[element[0]][element[1]] = segment_elements[
                        segment_elements.index(qualifier) + 1
                    ]
                else:
                    order[element[0]][element[1]] = segment_elements[position]
    return order


def map_order_detail(segment_id, segment_elements, this_line, file_line_number):

    for (segment, position, el_type), element in EDI850_order_detail_map.items():
        if segment_id == segment:
            if len(element) == 1:
                try:
                    if el_type == "int":
                        this_line[element[0]] = int(segment_elements[position])
                    elif el_type == "decimal":
                        this_line[element[0]] = Decimal(segment_elements[position])
                    elif el_type.startswith("after:"):
                        qualifier = el_type.split(":")[1]
                        this_line[element[0]] = segment_elements[
                            segment_elements.index(qualifier) + 1
                        ]
                    else:
                        this_line[element[0]] = segment_elements[position]

                except (ValueError, InvalidOperation) as e:
                    print(f"Line {file_line_number}: skipped PO1 ({e})")
                    return False
    return True


def is_850_file(segment_id, segment_elements):
    """Check if the file is a valid 850 EDI file based on the ST segment."""
    return (
        segment_id == "ST"
        and len(segment_elements) > 0
        and segment_elements[0] == "850"
    )


def parse_850(file_path):

    this_line = {
        "line_no": None,
        "qty": None,
        "uom": None,
        "price": None,
        "item": None,
        "description": None,
    }

    order = {
        "guid": None,
        "po_number": None,
        "po_date": None,
        "ship_to": {},
        "lines": [],
    }
    po_lines = []

    po_lines.clear()  # Clear the list of PO lines before parsing a new file
    current_line = None

    try:
        f = open(file_path)
    except FileNotFoundError as e1:
        print(f"File Access Error: {e1}")
        raise SystemExit(1)  # Exit the program if the file is not found

    is_format_850 = False
    with f:
        for file_line_number, line in enumerate(f, start=1):

            segment_id, segment_elements = parse_segment(line)
            if segment_id is None:
                continue
            elif segment_id == "ST":
                is_format_850 = is_850_file(segment_id, segment_elements)
            elif is_format_850:
                if segment_id == "PO1":
                    this_line = {}
                    if map_order_detail(
                        segment_id, segment_elements, this_line, file_line_number
                    ):
                        po_lines.append(this_line)
                    else:
                        print(
                            f"Line {file_line_number}: skipped PO1 segment due to mapping error."
                        )
                        this_line = None
                elif segment_id == "PID" and this_line is not None:
                    map_order_detail(
                        segment_id, segment_elements, this_line, file_line_number
                    )
                    po_lines[-1] = (
                        this_line  # Update the last line with the description
                    )

                else:
                    order = map_order_header(
                        segment_id, segment_elements, file_line_number
                    )

    if is_format_850:
        order["guid"] = "GU_" + str(
            uuid.uuid4()
        )  # Generate a unique GUID for the order
        order["lines"] = po_lines
        return order
    else:
        return None  # Return None if the file is not a valid 850 EDI file


if __name__ == "__main__":
    try:
        pi_input_file = sys.argv[1]
        pi_output_file = sys.argv[2] if len(sys.argv) > 2 else "order.json"

    except IndexError as e:
        print(
            f"Missing input 850 file path as parameter. Usage: {sys.argv[0]} <path_to_850_file>"
        )
        raise SystemExit(1)  # Exit the program if no file path is provided

    order = parse_850(pi_input_file)  # "d:/GetAI/sample.850")
    if order is None:
        print(f"File {pi_input_file} is not a valid 850 EDI file.")
        raise SystemExit(1)  # Exit the program if the file is not a valid 850 EDI file

    print(
        f"Total lines processed: {len(order['lines'])} for PO number: {order['po_number']} under guid: {order['guid']}"
    )
    print_po_lines(order["lines"])

    with open(pi_output_file, "w") as out:
        json.dump(order, out, indent=2, default=str)
