# regulat import
from decimal import Decimal, InvalidOperation
from datetime import datetime
import uuid

# custom imports
from edi_maps import EDI850_order_header_map, EDI850_order_detail_map


def parse_segment(line):
    """Return (segment_id, elements) for an EDI line, or (None, None) if blank."""
    line = line.strip().rstrip("~")
    if not line:
        return None, None
    elements = line.split("*")
    return elements[0], elements[1:]


def map_order_header(order, segment_id, segment_elements, file_line_number):

    for (segment, position, el_type), element in EDI850_order_header_map.items():
        if segment_id == segment:
            try:
                if len(element) == 1:

                    if el_type == "date":
                        order[element[0]] = datetime.strptime(
                            segment_elements[position], "%Y%m%d"
                        ).date()  # convert to date object
                    else:
                        order[element[0]] = segment_elements[position]

                else:
                    if el_type.startswith("if:"):
                        qualifier = el_type.split(":")[1]
                        if segment_elements[0] == qualifier:
                            order[element[0]][element[1]] = segment_elements[position]
                    else:
                        order[element[0]][element[1]] = segment_elements[position]
            except (ValueError, IndexError) as e:
                print(f"Line {file_line_number}: skipped {segment_id} ({e})")


def map_order_detail(segment_id, segment_elements, current_line, file_line_number):

    for (segment, position, el_type), element in EDI850_order_detail_map.items():
        if segment_id == segment:
            if len(element) == 1:
                try:
                    if el_type == "int":
                        current_line[element[0]] = int(segment_elements[position])
                    elif el_type == "decimal":
                        current_line[element[0]] = Decimal(segment_elements[position])
                    elif el_type.startswith("after:"):
                        qualifier = el_type.split(":")[1]
                        current_line[element[0]] = segment_elements[
                            segment_elements.index(qualifier) + 1
                        ]
                    else:
                        current_line[element[0]] = segment_elements[position]

                except (ValueError, InvalidOperation, IndexError) as e:
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

    order = {
        "guid": None,
        "po_number": None,
        "po_date": None,
        "ship_to": {},
        "lines": [],
    }
    po_lines = []

    current_line = None

    f = open(file_path)

    is_format_850 = False
    address_type = None

    with f:
        for file_line_number, line in enumerate(f, start=1):

            segment_id, segment_elements = parse_segment(line)
            if segment_id is None:
                continue
            elif segment_id == "ST":
                is_format_850 = is_850_file(segment_id, segment_elements)
            elif is_format_850:

                if segment_id == "PO1":
                    current_line = {}
                    if map_order_detail(
                        segment_id, segment_elements, current_line, file_line_number
                    ):
                        po_lines.append(current_line)
                    else:
                        current_line = None

                elif segment_id == "PID" and current_line is not None:
                    map_order_detail(
                        segment_id, segment_elements, current_line, file_line_number
                    )
                elif segment_id == "N1":
                    address_type = segment_elements[0] if segment_elements else None

                    map_order_header(
                        order, segment_id, segment_elements, file_line_number
                    )
                elif segment_id in ["N3", "N4"] and address_type != "ST":
                    continue
                else:
                    map_order_header(
                        order, segment_id, segment_elements, file_line_number
                    )

    if is_format_850:
        order["guid"] = "GU_" + str(
            uuid.uuid4()
        )  # Generate a unique GUID for the order
        order["lines"] = po_lines
        return order
    else:
        return None  # Return None if the file is not a valid 850 EDI file
