from urllib.parse import urlparse
import ipaddress
import pandas as pd


def parse_url(url):
    url = str(url).strip()

    if "://" not in url:
        url = "http://" + url

    return urlparse(url)


def extract_features(url):
    url = str(url)
    parsed = parse_url(url)

    hostname = parsed.hostname or ""

    try:
        ipaddress.ip_address(hostname)
        ip_address = 1
    except (ValueError, TypeError):
        ip_address = 0

    try:
        port = parsed.port
        has_port = int(port is not None)
    except ValueError:
        has_port = 0

    parts = hostname.split(".")
    subdomain_count = 0 if len(parts) <= 2 else len(parts) - 2

    features = {
        "url_length": len(url),
        "hostname_length": len(hostname),
        "path_length": len(parsed.path or ""),
        "query_length": len(parsed.query or ""),
        "num_dots": url.count("."),
        "num_hyphens": url.count("-"),
        "num_underscores": url.count("_"),
        "num_slashes": url.count("/"),
        "num_question_marks": url.count("?"),
        "num_equals": url.count("="),
        "num_ampersands": url.count("&"),
        "num_at_symbols": url.count("@"),
        "num_percent_symbols": url.count("%"),
        "num_colons": url.count(":"),
        "num_digits": sum(c.isdigit() for c in url),
        "num_letters": sum(c.isalpha() for c in url),
        "https": int(url.lower().startswith("https://")),
        "http": int(url.lower().startswith("http://")),
        "ip_address": ip_address,
        "subdomain_count": subdomain_count,
        "has_port": has_port,
        "has_query": int(bool(parsed.query)),
        "has_fragment": int(bool(parsed.fragment)),
        "has_login": int("login" in url.lower()),
        "has_verify": int("verify" in url.lower()),
        "has_account": int("account" in url.lower()),
        "has_secure": int("secure" in url.lower()),
        "has_update": int("update" in url.lower()),
        "has_password": int("password" in url.lower()),
        "has_bank": int("bank" in url.lower()),
        "has_free": int("free" in url.lower()),
        "has_bonus": int("bonus" in url.lower()),
        "has_confirm": int("confirm" in url.lower()),
        "has_payment": int("payment" in url.lower()),
        "has_wallet": int("wallet" in url.lower()),
        "has_auth": int("auth" in url.lower()),
    }

    return features


urls = [
    "https://www.google.com",
    "en.wikipedia.org/wiki/North_Dakota",
]

for url in urls:
    print("\n" + "=" * 60)
    print("URL:", url)
    print("=" * 60)

    features = extract_features(url)

    for name, value in features.items():
        print(f"{name}: {value}")