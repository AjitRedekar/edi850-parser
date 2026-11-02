EDI850_order_header_map = {
    ("BEG", 2, "str"): ("po_number",),
    ("BEG", 4, "date"): ("po_date",),
    ("N1", 1, "if:ST"): (
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
