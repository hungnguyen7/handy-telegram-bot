from urllib import error, parse, request


API_BASE_URL = "https://tinyurl.com/api-create.php"


def extract_url(text):
    if not text or not text.strip():
        return None, "Provide a URL to shorten."

    url = None
    for token in text.split():
        candidate = token.strip("\t\n\r <>[](){}\"'.,;")
        if not candidate:
            continue

        if candidate.startswith(("http://", "https://")):
            url = candidate
            break

        if "." in candidate:
            url = f"https://{candidate}"
            break

    if not url:
        return None, "Provide a URL to shorten."

    parsed = parse.urlparse(url)
    if parsed.scheme not in {"http", "https"} or not parsed.netloc:
        return None, "Provide a valid URL (include http:// or https://)."

    return url, None


def fetch_short_url(url):
    query = parse.urlencode({"url": url})
    api_url = f"{API_BASE_URL}?{query}"

    try:
        with request.urlopen(api_url, timeout=10) as response:
            short_url = response.read().decode("utf-8").strip()
    except error.URLError:
        return None, "Unable to reach URL shortener service."

    if not short_url or short_url.lower().startswith("error"):
        return None, "URL shortener service error."

    return short_url, None


def build_shortener_response(text):
    url, error_message = extract_url(text)
    if error_message:
        return None, error_message

    short_url, error_message = fetch_short_url(url)
    if error_message:
        return None, error_message

    response = f"Short URL: {short_url}"
    return response, None
