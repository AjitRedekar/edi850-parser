from decimal import Decimal
import json

segments = {
    "ISA": "Interchange control header",
    "GS": "Functional group header",
    "ST": "Transaction set header",
    "BEG": "Beginning segment for purchase order",
    "REF": "Reference identification",
    "DTM": "Date/time reference",
    "N1": "Party identification",
    "N3": "Address line",
    "N4": "Geographic location",
    "PO1": "Baseline item data (order line)",
    "PID": "Product description",
    "CTT": "Transaction totals",
    "SE": "Transaction set trailer",
    "GE": "Functional group trailer",
    "IEA": "Interchange control trailer",
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


segment_count = 0
po_lines = []

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

        segment_count += 1

        print(
            f"#{segment_count}: {segment_id}, {segments.get(segment_id, 'Unknown segment')}"
        )

        if segment_id == "PO1":
            try:
                po_lines.append(
                    {
                        "line_no": int(segment_elements[0]),
                        "qty": int(segment_elements[1]),
                        "uom": segment_elements[2],
                        "price": Decimal(segment_elements[3]),
                    }
                )

            except ValueError as e:
                print(f"Line {file_line_number}: skipped PO1, bad value ({e})")

print(f"Total segments: {segment_count}")
print(f"PO lines: {len(po_lines)}")
print_po_lines(po_lines)

with open("d:/GetAI/order.json", "w") as out:
    json.dump(po_lines, out, indent=2, default=str)
