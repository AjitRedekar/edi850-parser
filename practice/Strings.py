po_number = "PO-004512"
qty = 25
price = 12.50

# Python works out the type from the value; no dcl-s needed
print(type(po_number), type(qty), type(price))

# slicing works like %subst, but positions start at 0 and the end is excluded 
print(po_number[3:9])  # prints 00451
print(po_number[-6:])  # prints 004512

# buildings strings (like concatenation with +) 
total = qty * price 
print(f"Order {po_number}: {qty} x {price} = {total}")  

# common string methods
print(" ABC  Corp ".strip()) # like %trim 
print("abc corp".upper()) # like %upper
print(po_number.replace("PO-", "")) # like %replace

from datetime import datetime 

seg = "BEG*00*SA*    4500123456 **20261023"
elements = seg.strip().split("*") 
po_number = elements[3].strip()
# po_date = elements[5].strip()
po_date = datetime.strptime(elements[5].strip(), "%Y%m%d").date()  # convert to date object


print(f"segment has PO number : {po_number} with date : {po_date}")
print(f"PO Date refers to {po_date.strftime('%A, %B %d, %Y')}")  # like %date