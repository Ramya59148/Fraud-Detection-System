from urllib.parse import urlparse
import re


FEATURE_NAMES = [
    "url_length",
    "hostname_length",
    "path_length",
    "query_length",
    "num_dots",
    "num_hyphens",
    "num_underscores",
    "num_question_marks",
    "num_equals",
    "num_ampersands",
    "num_at_symbols",
    "num_percent_symbols",
    "num_digits",
    "num_letters",
    "https",
    "ip_address",
    "subdomain_count",
    "has_port",
    "has_query",
    "has_fragment",
    "has_login",
    "has_verify",
    "has_account",
    "has_secure",
    "has_update",
    "has_password",
    "has_bank",
    "has_free",
    "has_bonus",
    "has_confirm",
    "has_payment",
    "has_wallet",
    "has_auth",
]


def parse_url(url):
    """
    Parse a URL while preserving the original URL string.

    URLs without a scheme are parsed internally as HTTP,
    but the original string is used for raw character features.
    """
    url = str(url).strip()

    if not url:
        return None

    try:
        parsed_url = url

        if "://" not in parsed_url:
            parsed_url = "http://" + parsed_url

        return urlparse(parsed_url)

    except (ValueError, TypeError):
        return None


def extract_features(url):
    """
    Extract exactly 33 features from a URL.

    IMPORTANT:
    Raw character features use the original URL.
    Parsed URL features use the internally normalized URL.
    """

    url = str(url).strip()

    parsed = parse_url(url)

    if parsed is None:
        hostname = ""
        path = ""
        query = ""
        fragment = ""
        port = None
    else:
        hostname = parsed.hostname or ""
        path = parsed.path or ""
        query = parsed.query or ""
        fragment = parsed.fragment or ""

        try:
            port = parsed.port
        except ValueError:
            port = None

    hostname_parts = hostname.split(".") if hostname else []

    # Remove empty hostname components
    hostname_parts = [part for part in hostname_parts if part]

    subdomain_count = max(len(hostname_parts) - 2, 0)

    # Detect IPv4 address
    ip_address = int(
        bool(
            re.fullmatch(
                r"(?:\d{1,3}\.){3}\d{1,3}",
                hostname
            )
        )
    )

    url_lower = url.lower()

    features = [
        len(url),
        len(hostname),
        len(path),
        len(query),

        url.count("."),
        url.count("-"),
        url.count("_"),
        url.count("?"),
        url.count("="),
        url.count("&"),
        url.count("@"),
        url.count("%"),

        sum(char.isdigit() for char in url),
        sum(char.isalpha() for char in url),

        int(url_lower.startswith("https://")),

        ip_address,

        subdomain_count,

        int(port is not None),
        int(bool(query)),
        int(bool(fragment)),

        int("login" in url_lower),
        int("verify" in url_lower),
        int("account" in url_lower),
        int("secure" in url_lower),
        int("update" in url_lower),
        int("password" in url_lower),
        int("bank" in url_lower),
        int("free" in url_lower),
        int("bonus" in url_lower),
        int("confirm" in url_lower),
        int("payment" in url_lower),
        int("wallet" in url_lower),
        int("auth" in url_lower),
    ]

    if len(features) != len(FEATURE_NAMES):
        raise ValueError(
            f"Expected {len(FEATURE_NAMES)} features, "
            f"but generated {len(features)}"
        )

    return features
