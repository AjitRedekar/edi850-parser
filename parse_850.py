from decimal import Decimal
import json

emap = {
    "po_number": {"label": "po_number", "segment": "BEG", "position": 2, "value": None},
    "po_date": {"label": "po_date", "segment": "BEG", "position": 4, "value": None},
    "ship_to.name": {"label": "name", "segment": "N1", "position": 1, "value": None},
    "ship_to.address": {
        "label": "address",
        "segment": "N3",
        "position": 0,
        "value": None,
    },
    "ship_to.city": {"label": "city", "segment": "N4", "position": 0, "value": None},
    "ship_to.state": {"label": "state", "segment": "N4", "position": 1, "value": None},
    "ship_to.zip": {"label": "zip", "segment": "N4", "position": 2, "value": None},
    "line_no": {"label": "line_no", "segment": "PO1", "position": 0, "value": None},
    "line_qty": {"label": "qty", "segment": "PO1", "position": 1, "value": None},
    "line_uom": {"label": "uom", "segment": "PO1", "position": 2, "value": None},
    "line_price": {"label": "price", "segment": "PO1", "position": 3, "value": None},
    "line_item": {"label": "item", "segment": "PO1", "position": 6, "value": None},
    "line_description": {
        "label": "description",
        "segment": "PID",
        "position": 4,
        "value": None,
    },
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

        if segment_id == emap.get("po_number").get("segment"):
            emap.get("po_number").update(
                {"value": segment_elements[emap.get("po_number").get("position")]}
            )

        if segment_id == emap.get("po_date").get("segment"):
            emap.get("po_date").update(
                {"value": segment_elements[emap.get("po_date").get("position")]}
            )

        if segment_id == emap.get("ship_to.name").get("segment"):
            emap.get("ship_to.name").update(
                {"position": segment_elements.index("ST") + 1}
            )

            emap.get("ship_to.name").update(
                {"value": segment_elements[emap.get("ship_to.name").get("position")]}
            )

        if segment_id == emap.get("ship_to.address").get("segment"):
            emap.get("ship_to.address").update(
                {"value": segment_elements[emap.get("ship_to.address").get("position")]}
            )

        if segment_id == emap.get("ship_to.city").get("segment"):
            emap.get("ship_to.city").update(
                {"value": segment_elements[emap.get("ship_to.city").get("position")]}
            )

        if segment_id == emap.get("ship_to.state").get("segment"):
            emap.get("ship_to.state").update(
                {"value": segment_elements[emap.get("ship_to.state").get("position")]}
            )

        if segment_id == emap.get("ship_to.zip").get("segment"):
            emap.get("ship_to.zip").update(
                {"value": segment_elements[emap.get("ship_to.zip").get("position")]}
            )

        if segment_id == emap.get("line_no").get("segment"):
            current_line = None  # forget the previous line
            try:
                current_line = {
                    emap.get("line_no").get("label"): int(
                        segment_elements[emap.get("line_no").get("position")]
                    ),
                    emap.get("line_qty").get("label"): int(
                        segment_elements[emap.get("line_qty").get("position")]
                    ),
                    emap.get("line_uom").get("label"): segment_elements[
                        emap.get("line_uom").get("position")
                    ],
                    emap.get("line_price").get("label"): Decimal(
                        segment_elements[emap.get("line_price").get("position")]
                    ),
                    emap.get("line_item").get("label"): segment_elements[
                        segment_elements.index("VP") + 1
                    ],
                }
                po_lines.append(current_line)
            except ValueError as e:
                print(f"Line {file_line_number}: skipped PO1 ({e})")

        elif (
            segment_id == emap.get("line_description").get("segment")
            and current_line is not None
        ):
            current_line[emap.get("line_description").get("label")] = segment_elements[
                emap.get("line_description").get("position")
            ]


po_header.append(
    {
        emap.get("po_number").get("label"): emap.get("po_number").get("value"),
        emap.get("po_date").get("label"): emap.get("po_date").get("value"),
        "ship_to": {
            emap.get("ship_to.name")
            .get("label"): emap.get("ship_to.name")
            .get("value"),
            emap.get("ship_to.address")
            .get("label"): emap.get("ship_to.address")
            .get("value"),
            emap.get("ship_to.city")
            .get("label"): emap.get("ship_to.city")
            .get("value"),
            emap.get("ship_to.state")
            .get("label"): emap.get("ship_to.state")
            .get("value"),
            emap.get("ship_to.zip").get("label"): emap.get("ship_to.zip").get("value"),
        },
        "lines": po_lines,
    }
)


with open("d:/GetAI/order.json", "w") as out:
    json.dump(po_header, out, indent=2, default=str)
