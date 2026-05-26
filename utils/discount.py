import re


def format_number(value):
    if abs(value - round(value)) < 1e-9:
        return f"{int(round(value)):,}"
    return f"{value:,.2f}"


def parse_discount_input(text):
    numbers = re.findall(r"\d+(?:[.,]\d+)?", text or "")
    if len(numbers) < 2:
        return None, None, "Provide input as: <percent> <max VND>. Example: 10 50000"

    rate = float(numbers[0].replace(",", ""))
    max_discount = float(numbers[1].replace(",", ""))

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
