import json
import re
from urllib import error, request


API_URL = "https://open.er-api.com/v6/latest/{}"
SUPPORTED_CURRENCIES = {"USD", "EUR", "JPY", "CNY"}


def format_number(value):
    if abs(value - round(value)) < 1e-9:
        return f"{int(round(value)):,}"
    return f"{value:,.2f}"


def parse_currency_input(text):
    if not text:
        return None, None, "Provide input as: <amount> <currency>. Example: 100 USD"

    currency_match = re.search(r"\b(usd|eur|jpy|cny)\b", text, re.IGNORECASE)
    if not currency_match:
        supported = ", ".join(sorted(SUPPORTED_CURRENCIES))
        return None, None, f"Supported currencies: {supported}."

    currency = currency_match.group(1).upper()
    amount_match = re.search(r"\d+(?:[.,]\d+)?", text)
    if not amount_match:
        return None, None, "Provide a numeric amount. Example: 100 USD"

    amount = float(amount_match.group(0).replace(",", ""))
    if amount <= 0:
        return None, None, "Amount must be greater than 0."

    return amount, currency, None


def fetch_rate_to_vnd(currency):
    url = API_URL.format(currency)
    try:
        with request.urlopen(url, timeout=10) as response:
            payload = json.loads(response.read().decode("utf-8"))
    except error.URLError:
        return None, "Unable to reach exchange rate service."
    except json.JSONDecodeError:
        return None, "Invalid response from exchange rate service."

    if payload.get("result") != "success":
        return None, "Exchange rate service error."

    rates = payload.get("rates", {})
    vnd_rate = rates.get("VND")
    if not vnd_rate:
        return None, "VND rate is unavailable right now."

    return float(vnd_rate), None


def build_currency_response(text):
    amount, currency, error_message = parse_currency_input(text)
    if error_message:
        return None, error_message

    rate, error_message = fetch_rate_to_vnd(currency)
    if error_message:
        return None, error_message

    converted = amount * rate
    amount_text = format_number(amount)
    converted_text = format_number(converted)
    rate_text = format_number(rate)

    response = (
        f"{amount_text} {currency} -> {converted_text} VND\n"
        f"Exchange rate: 1 {currency} = {rate_text} VND"
    )
    return response, None
