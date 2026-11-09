# standard library imports
import sys
import json
import os
from dataclasses import asdict
from dotenv import load_dotenv

load_dotenv()  # Load environment variables from .env file

# custom imports
from edi850 import parse_850
from api_post import post_order


def print_po_lines(po_lines):
    """Print PO1 details as an aligned table."""

    print(f"{'Line':>4} {'Qty':>5} {'UOM':<4} {'Price':>8} {'Cost':>10}")

    for line in po_lines:
        print(
            f"{line.line_no:>4} {line.qty:>5} {line.uom:<4} "
            f"{line.price:>8.2f} {line.extended_value() :>10.2f}"
        )  # total price


if __name__ == "__main__":
    try:
        pi_input_file = sys.argv[1]
        pi_output_file = sys.argv[2] if len(sys.argv) > 2 else "order.json"

    except IndexError:
        print(
            f"Missing input 850 file path as parameter. Usage: {sys.argv[0]} <path_to_850_file>"
        )
        raise SystemExit(1)  # Exit the program if no file path is provided

    try:
        order = parse_850(pi_input_file)
    except OSError as e:
        print(f"File Access Error: {e}")
        raise SystemExit(1)  # Exit the program if the file is not found

    if order is None:
        print(f"File {pi_input_file} is not a valid 850 EDI file.")
        raise SystemExit(1)  # Exit the program if the file is not a valid 850 EDI file

    print(
        f"Total lines processed: {len(order.lines)} for PO number: {order.po_number} under guid: {order.guid}"
    )
    print_po_lines(order.lines)

    with open(pi_output_file, "w") as out:
        json.dump(asdict(order), out, indent=2, default=str)

    payload = json.loads(json.dumps(asdict(order), default=str))

    url = os.environ.get(
        "ORDER_API_URL", "https://httpbin.org/post"
    )  # Default to httpbin for testing
    api_key = os.environ.get("ORDER_API_KEY")  # None if not found.
    if api_key is None:
        print("Missing ORDER_API_KEY in environment variables.")
        raise SystemExit(1)  # Exit the program if the API key is not found

    elif post_order(url, api_key, payload):
        # Post the order to the API endpoint
        print(f"Order posted successfully.")
    else:
        raise SystemExit(1)  # Exit the program if the order post fails
