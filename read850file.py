# segmentCount = 0
# POlineCount = 0
# lineArray = []
# lineArray.append(f"lineNo : quantity : UOM : price")  # header for table

# for line in open("d:/GetAI/sample.850"):
#     elements = line.strip().rstrip('~').split("*")
#     segmentId = elements[0].strip()

#     segmentCount += 1
#     # print segment id, its number and number of elements in it
#     print(f"#{segmentCount}: Segment id {segmentId} has {len(elements)} elements")

#     # detect PO line segment
#     if segmentId == "PO1":
#         POlineCount += 1
#         # save line info in aarray for later printing
#         lineArray.append(f"{elements[1].strip()} : {elements[2].strip()} : {elements[3].strip()} : {elements[4].strip()}")


# print(f"Total segments in file : {segmentCount}")
# print(f"PO lines: {POlineCount}")

# for line in lineArray:
#     print(line)


# segment_count = 0
# po_lines = []

# with open("d:/GetAI/sample.850") as f:
#     for line in f:
#         line = line.strip().rstrip("~")
#         if not line:
#             continue                      # skip blank lines

#         elements = line.split("*")
#         segment_id = elements[0]
#         segment_count += 1
#         print(f"#{segment_count}: {segment_id} has {len(elements)} elements")

#         if segment_id == "PO1":
#             # keep the raw values; decide formatting later
#             po_lines.append(elements[1:5])  # line no, qty, UOM, price

# print(f"Total segments: {segment_count}")
# print(f"PO lines: {len(po_lines)}")

# print(f"{'Line':>4} {'Qty':>5} {'UOM':<4} {'Price':>8}")
# for line_no, qty, uom, price in po_lines:
#     print(f"{line_no:>4} {qty:>5} {uom:<4} {price:>8}")


# using functions
# parse_segment(line)

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
    with open("d:/GetAI/bad.850") as f:
        for line in f:

            segment_id, segment_elements = parse_segment(line)
            if segment_id is None:
                continue

            segment_count += 1

            print(
                f"#{segment_count}: {segment_id}, {segments.get(segment_id, 'Unknown segment')}"
            )

            try:

                if segment_id == "PO1":
                    po_lines.append(
                        {
                            "line_no": int(segment_elements[0]),
                            "qty": int(segment_elements[1]),
                            "uom": segment_elements[2],
                            "price": Decimal(segment_elements[3]),
                        }
                    )

            except ValueError as e2:
                print(f"Data Conversion Error: {e2} at PO line {segment_elements[0]}")
                continue  # skip this line and continue processing

    print(f"Total segments: {segment_count}")
    print(f"PO lines: {len(po_lines)}")
    print_po_lines(po_lines)

    with open("d:/GetAI/order.json", "w") as out:
        json.dump(po_lines, out, indent=2, default=str)

except FileNotFoundError as e1:
    print(f"File Access Error: {e1}")
