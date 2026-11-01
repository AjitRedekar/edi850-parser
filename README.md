parse_850.py is a Python script that parses EDI 850 Purchase Order files. 
It extracts relevant information from the EDI file and converts it into a JSON format. 
The script can handle various segments and elements of the EDI 850 standard, 
    making it useful for businesses that need to process purchase orders electronically.
for each document it genereates GUID value in the format of GU_DateTimeStamp, where DateTimeStamp is the current date and time in the format YYYYMMDDHHMMSSssssss.

call example:
1st parameter is the path to the EDI 850 file to be parsed.
2nd parameter is optional, if provided it will be the path to the output JSON file. If not provided, th default output file will be named "output.json".

```python
    parse_850.py "sample.850"