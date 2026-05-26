import re


TOKEN_PATTERN = re.compile(r"(?P<number>\d+(?:[.,]\d+)?)\s*(?P<suffix>[kK])?\s*(?P<percent>%)?")


def format_number(value):
    if abs(value - round(value)) < 1e-9:
        return f"{int(round(value)):,}"
    return f"{value:,.2f}"


def parse_discount_input(text):
    tokens = []
    for match in TOKEN_PATTERN.finditer(text or ""):
        number = float(match.group("number").replace(",", ""))
        suffix = match.group("suffix")
        is_percent = bool(match.group("percent"))

        if is_percent:
            value = number
        else:
            value = number * 1000 if suffix else number

        tokens.append((value, is_percent))

    percent_tokens = [value for value, is_percent in tokens if is_percent]
    amount_tokens = [value for value, is_percent in tokens if not is_percent]

    if percent_tokens:
        rate = percent_tokens[0]
        max_discount = amount_tokens[0] if amount_tokens else None
    else:
        if len(tokens) < 2:
            return None, None, "Provide input as: <percent> <max VND>. Examples: 10 50000, 10% 50k"
        rate = tokens[0][0]
        max_discount = tokens[1][0]

    if max_discount is None:
        return None, None, "Provide input as: <percent> <max VND>. Examples: 10 50000, 10% 50k"

    if rate <= 0 or max_discount <= 0:
        return None, None, "Percent and max discount must be greater than 0."

    return rate, max_discount, None


def build_discount_response(text):
    rate, max_discount, error = parse_discount_input(text)
    if error:
        return None, error

    purchase_amount = max_discount * 100 / rate
    purchase_text = format_number(purchase_amount)
    discount_text = format_number(max_discount)

    response = (
        f"Optimal purchase amount: {purchase_text} VND\n"
        f"Max discount applied: {discount_text} VND at {rate}%"
    )
    return response, None
