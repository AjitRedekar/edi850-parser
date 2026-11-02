# standard library imports
import sys
import json

# custom imports
from edi850 import parse_850


def print_po_lines(po_lines):
    """Print PO1 details as an aligned table."""
    print(f"{'Line':>4} {'Qty':>5} {'UOM':<4} {'Price':>8} {'Cost':>10}")
    for po_line in po_lines:
        print(
            f"{po_line.get('line_no'):>4} {po_line.get('qty'):>5} {po_line.get('uom'):<4} {po_line.get('price'):>8.2f} {po_line.get('qty') * po_line.get('price'):>10.2f}"
        )  # total price


if __name__ == "__main__":
    try:
        pi_input_file = sys.argv[1]
        pi_output_file = sys.argv[2] if len(sys.argv) > 2 else "order.json"

    except IndexError as e:
        print(
            f"Missing input 850 file path as parameter. Usage: {sys.argv[0]} <path_to_850_file>"
        )
        raise SystemExit(1)  # Exit the program if no file path is provided

    try:
        order = parse_850(pi_input_file)  # "d:/GetAI/sample.850")
    except OSError as e:
        print(f"File Access Error: {e}")
        raise SystemExit(1)  # Exit the program if the file is not found

    if order is None:
        print(f"File {pi_input_file} is not a valid 850 EDI file.")
        raise SystemExit(1)  # Exit the program if the file is not a valid 850 EDI file

    print(
        f"Total lines processed: {len(order['lines'])} for PO number: {order['po_number']} under guid: {order['guid']}"
    )
    print_po_lines(order["lines"])

    with open(pi_output_file, "w") as out:
        json.dump(order, out, indent=2, default=str)
