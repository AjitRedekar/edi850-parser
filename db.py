import sqlite3

from datetime import date
from decimal import Decimal

from models import Address, Order, OrderLine

SCHEMA = """
create table if not exists order_header (
    guid text primary_key,
    po_number text unique not null,
    po_date text,
    ship_name text,
    ship_address text,
    ship_city text,
    ship_state text,
    ship_zip text,
    declared_line_count integer
);
create table if not exists order_line (
    guid text not null references order_header
    , line_no integer not null
    , qty integer not null
    , uom text
    , price text not null
    , item text
    , description text
    , primary key (guid, line_no)
);
"""


def init_db(conn: sqlite3.Connection) -> None:
    """Create the tables if they don't exist yet."""
    conn.executescript(SCHEMA)


def save_order(conn: sqlite3.Connection, order: Order) -> None:
    """Save the order header and its lines as one transaction."""
    with conn:
        conn.execute(
            "INSERT INTO order_header "
            "(guid, po_number, po_date, "
            "ship_name, ship_address, ship_city, ship_state, ship_zip, "
            "declared_line_count) "
            "VALUES (?, ?, ?, ?, ?, ?, ?, ?,?)",
            (
                order.guid,
                order.po_number,
                str(order.po_date),
                order.ship_to.name,
                order.ship_to.address,
                order.ship_to.city,
                order.ship_to.state,
                order.ship_to.zip,
                order.declared_line_count,
            ),
        )
        for line in order.lines:
            conn.execute(
                "insert into order_line (guid, line_no, qty, uom, price, item, description)"
                "values (?,?,?,?,?,?,?)",
                (
                    order.guid,
                    line.line_no,
                    line.qty,
                    line.uom,
                    str(line.price),
                    line.item,
                    line.description,
                ),
            )


def load_order(conn: sqlite3.Connection, guid: str) -> Order | None:

    conn.row_factory = sqlite3.Row

    header = conn.execute(
        "select * from order_header where guid =?", (guid,)
    ).fetchone()

    if header is None:
        return None

    order = Order(
        guid=header["guid"],
        po_number=header["po_number"],
        po_date=(date.fromisoformat(header["po_date"]) if header["po_date"] else None),
        ship_to=Address(
            name=header["ship_name"],
            address=header["ship_address"],
            city=header["ship_city"],
            state=header["ship_state"],
            zip=header["ship_zip"],
        ),
        declared_line_count=header["declared_line_count"],
    )

    for row in conn.execute(
        "select * from order_line where guid =? order by line_no", (guid,)
    ):
        order.lines.append(
            OrderLine(
                line_no=row["line_no"],
                qty=row["qty"],
                uom=row["uom"],
                price=Decimal(row["price"]),
                item=row["item"],
                description=row["description"],
            )
        )
    return order
