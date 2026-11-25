def valiate_order(order):
    """return list of problems found in the order. empty means valid."""
    problems = []

    if not order.ship_to.name:
        problems.append("Missing ship-to name")

    if not order.ship_to.city:
        problems.append("Missing ship-to city")

    for line in order.lines:
        if line.qty <= 0:
            problems.append(f"Line {line.line_no}: quantity is {line.qty}")

        if line.price <= 0:
            problems.append(f"Line {line.line_no}: price is {line.price}")

    if order.declared_line_count != len(order.lines):
        problems.append(
            f"declared line count {order.declared_line_count} not matching with number of lines {len(order.lines)} processed"
        )

    return problems
