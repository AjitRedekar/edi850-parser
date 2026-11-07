main.py is a Python script that parses EDI 850 Purchase Order files. 
* It extracts relevant information from the EDI file and converts it into a JSON format. 
* The script can handle various segments and elements of the EDI 850 standard, 
    making it useful for businesses that need to process purchase orders electronically.
* for each document it generates GUID value in the format of GU_unique id.
* known limitation: 
  - the script is designed to parse only one EDI 850 document at a time.
  - the script parse only ship to address, it does not parse bill to address.
  - EDI 850 document is expected to be in format X12 004010 with * and ~ delimiters

* program structure:
```text
edi850-parser/
├── edi_maps.py      # the two map dictionaries only
├── edi850.py        # parse_segment, map_order_header, map_order_detail, is_850_file, parse_850
├── models.py        # the data models: Order, ShipTo, Line
└── main.py          # the __main__ part: arguments, print_po_lines, JSON output

```

call example:
1st parameter is the path to the EDI 850 file to be parsed.
2nd parameter is optional, if provided it will be the path to the output JSON file. If not provided, the default output file will be named "order.json".


```bash
    python main.py "tests/data/sample.850"
```

output example:
```json
{
  "guid": "GU_e2b25ea5-1b8c-4ed9-b910-7ccb5358b156",
  "po_number": "4500123456",
  "po_date": "2026-10-23",
  "ship_to": {
    "name": "ACME RETAIL DC 7",
    "address": "1200 INDUSTRIAL PKWY",
    "city": "COLUMBUS",
    "state": "OH",
    "zip": "43215"
  },
  "lines": [
    {
      "line_no": 1,
      "qty": 24,
      "uom": "EA",
      "price": "12.50",
      "item": "WC-1001",
      "description": "BLUE WIDGET 10MM"
    },
    {
      "line_no": 2,
      "qty": 10,
      "uom": "CA",
      "price": "48.00",
      "item": "WC-2040",
      "description": "WIDGET MOUNTING KIT"
    },
    {
      "line_no": 3,
      "qty": 0,
      "uom": "EA",
      "price": "7.25",
      "item": "WC-3300",
      "description": "WIDGET END CAP"
    }
  ]
}
```