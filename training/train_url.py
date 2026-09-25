# ==========================================
# SENTRIX - URL FEATURE EXTRACTION
# ==========================================

import os
import re
import ipaddress
import pandas as pd

from urllib.parse import urlparse


# ==========================================
# 1. PATHS
# ==========================================

BASE_DIR = os.path.dirname(
    os.path.dirname(
        os.path.abspath(__file__)
    )
)

INPUT_FILE = os.path.join(
    BASE_DIR,
    "dataSets",
    "clean_url_dataset.csv"
)

OUTPUT_FILE = os.path.join(
    BASE_DIR,
    "dataSets",
    "url_features.csv"
)


# ==========================================
# 2. LOAD DATASET
# ==========================================

print("=" * 60)
print("SENTRIX - URL FEATURE EXTRACTION")
print("=" * 60)

print("\nLoading dataset...")

df = pd.read_csv(INPUT_FILE)

print("\nDataset Loaded Successfully!")

print("\nDataset Shape:")
print(df.shape)

print("\nColumns:")
print(df.columns.tolist())

print("\nMissing Values:")
print(df.isnull().sum())


# ==========================================
# 3. CHECK REQUIRED COLUMNS
# ==========================================

if "url" not in df.columns:
    raise ValueError(
        "ERROR: 'url' column not found!"
    )

if "label" not in df.columns:
    raise ValueError(
        "ERROR: 'label' column not found!"
    )


# ==========================================
# 4. REMOVE MISSING VALUES
# ==========================================

df = df.dropna(
    subset=["url", "label"]
).copy()

df["url"] = df["url"].astype(str)

df["label"] = df["label"].astype(str).str.strip()

print("\nAfter removing missing values:")
print(df.shape)


# ==========================================
# 5. SAFE URL PARSER
# ==========================================

def parse_url(url):

    try:

        url = str(url).strip()

        if not url:
            return None

        if "://" not in url:
            url = "http://" + url

        return urlparse(url)

    except (ValueError, TypeError):

        return None


# ==========================================
# 6. BASIC FEATURES
# ==========================================

def get_url_length(url):

    return len(str(url))


def get_hostname_length(url):

    parsed = parse_url(url)

    if parsed is None:
        return 0

    return len(parsed.hostname or "")


def get_path_length(url):

    parsed = parse_url(url)

    if parsed is None:
        return 0

    return len(parsed.path or "")


def get_query_length(url):

    parsed = parse_url(url)

    if parsed is None:
        return 0

    return len(parsed.query or "")


# ==========================================
# 7. CHARACTER COUNT FEATURES
# ==========================================

def count_dots(url):

    return str(url).count(".")


def count_hyphens(url):

    return str(url).count("-")


def count_underscores(url):

    return str(url).count("_")


def count_question_marks(url):

    return str(url).count("?")


def count_equals(url):

    return str(url).count("=")


def count_ampersands(url):

    return str(url).count("&")


def count_at_symbols(url):

    return str(url).count("@")


def count_percent_symbols(url):

    return str(url).count("%")


# ==========================================
# 8. DIGIT / LETTER FEATURES
# ==========================================

def count_digits(url):

    return sum(
        character.isdigit()
        for character in str(url)
    )


def count_letters(url):

    return sum(
        character.isalpha()
        for character in str(url)
    )


# ==========================================
# 9. HTTPS FEATURE
# ==========================================

def has_https(url):

    return int(
        str(url).lower().startswith("https://")
    )


# ==========================================
# 10. IP ADDRESS FEATURE
# ==========================================

def has_ip_address(url):

    try:

        parsed = parse_url(url)

        if parsed is None:
            return 0

        hostname = parsed.hostname

        if not hostname:
            return 0

        ipaddress.ip_address(hostname)

        return 1

    except (ValueError, TypeError):

        return 0


# ==========================================
# 11. SUBDOMAIN FEATURE
# ==========================================

def count_subdomains(url):

    try:

        parsed = parse_url(url)

        if parsed is None:
            return 0

        hostname = parsed.hostname

        if not hostname:
            return 0

        parts = hostname.split(".")

        if len(parts) <= 2:
            return 0

        return len(parts) - 2

    except (ValueError, TypeError):

        return 0


# ==========================================
# 12. SUSPICIOUS KEYWORDS
# ==========================================

def contains_keyword(url, keyword):

    return int(
        keyword in str(url).lower()
    )


# ==========================================
# 13. SPECIAL URL FEATURES
# ==========================================

def has_port(url):

    try:

        parsed = parse_url(url)

        if parsed is None:
            return 0

        return int(
            parsed.port is not None
        )

    except (ValueError, TypeError):

        return 0


def has_fragment(url):

    parsed = parse_url(url)

    if parsed is None:
        return 0

    return int(
        bool(parsed.fragment)
    )


def has_query(url):

    parsed = parse_url(url)

    if parsed is None:
        return 0

    return int(
        bool(parsed.query)
    )


# ==========================================
# 14. EXTRACT ALL FEATURES
# ==========================================

def extract_features(url):

    url = str(url).strip()

    features = {

        # ------------------------------
        # Length
        # ------------------------------

        "url_length":
            get_url_length(url),

        "hostname_length":
            get_hostname_length(url),

        "path_length":
            get_path_length(url),

        "query_length":
            get_query_length(url),

        # ------------------------------
        # Characters
        # ------------------------------

        "num_dots":
            count_dots(url),

        "num_hyphens":
            count_hyphens(url),

        "num_underscores":
            count_underscores(url),

        "num_question_marks":
            count_question_marks(url),

        "num_equals":
            count_equals(url),

        "num_ampersands":
            count_ampersands(url),

        "num_at_symbols":
            count_at_symbols(url),

        "num_percent_symbols":
            count_percent_symbols(url),

        # ------------------------------
        # Digits / Letters
        # ------------------------------

        "num_digits":
            count_digits(url),

        "num_letters":
            count_letters(url),

        # ------------------------------
        # HTTPS
        # ------------------------------

        "https":
            has_https(url),

        # ------------------------------
        # IP
        # ------------------------------

        "ip_address":
            has_ip_address(url),

        # ------------------------------
        # Domain
        # ------------------------------

        "subdomain_count":
            count_subdomains(url),

        "has_port":
            has_port(url),

        "has_query":
            has_query(url),

        "has_fragment":
            has_fragment(url),

        # ------------------------------
        # Suspicious Keywords
        # ------------------------------

        "has_login":
            contains_keyword(url, "login"),

        "has_verify":
            contains_keyword(url, "verify"),

        "has_account":
            contains_keyword(url, "account"),

        "has_secure":
            contains_keyword(url, "secure"),

        "has_update":
            contains_keyword(url, "update"),

        "has_password":
            contains_keyword(url, "password"),

        "has_bank":
            contains_keyword(url, "bank"),

        "has_free":
            contains_keyword(url, "free"),

        "has_bonus":
            contains_keyword(url, "bonus"),

        "has_confirm":
            contains_keyword(url, "confirm"),

        "has_payment":
            contains_keyword(url, "payment"),

        "has_wallet":
            contains_keyword(url, "wallet"),

        "has_auth":
            contains_keyword(url, "auth")
    }

    return features


# ==========================================
# 15. TEST ONE URL
# ==========================================

print("\n")
print("=" * 60)
print("TESTING URL FEATURE EXTRACTION")
print("=" * 60)

sample_url = df["url"].iloc[0]

print("\nSample URL:")
print(sample_url)

sample_features = extract_features(sample_url)

print("\nExtracted Features:")

for feature, value in sample_features.items():

    print(
        f"{feature}: {value}"
    )


# ==========================================
# 16. EXTRACT FEATURES FOR ALL URLS
# ==========================================

print("\n")
print("=" * 60)
print("EXTRACTING FEATURES FROM ALL URLS")
print("=" * 60)

print(
    f"\nTotal URLs: {len(df):,}"
)

print("\nPlease wait...")

feature_data = []

for index, url in enumerate(df["url"]):

    feature_data.append(
        extract_features(url)
    )

    if (index + 1) % 50000 == 0:

        print(
            f"Processed: "
            f"{index + 1:,} / "
            f"{len(df):,}"
        )


# ==========================================
# 17. CREATE FEATURE DATAFRAME
# ==========================================

features_df = pd.DataFrame(
    feature_data
)

print("\nFeature extraction completed!")

print("\nFeature Dataset Shape:")
print(
    features_df.shape
)


# ==========================================
# 18. ADD LABEL
# ==========================================

features_df["label"] = df[
    "label"
].values


# ==========================================
# 19. DISPLAY FINAL DATASET
# ==========================================

print("\n")
print("=" * 60)
print("FINAL URL FEATURE DATASET")
print("=" * 60)

print("\nFirst 5 Rows:")

print(
    features_df.head()
)

print("\nColumns:")

print(
    features_df.columns.tolist()
)

print("\nNumber of Features:")

print(
    len(features_df.columns) - 1
)

print("\nLabels:")

print(
    features_df["label"].value_counts()
)


# ==========================================
# 20. SAVE FEATURE DATASET
# ==========================================

print("\n")
print("Saving feature dataset...")

features_df.to_csv(
    OUTPUT_FILE,
    index=False
)

print("\nFeature dataset saved successfully!")

print("\nSaved Location:")

print(
    OUTPUT_FILE
)


# ==========================================
# 21. FINAL MESSAGE
# ==========================================

print("\n")
print("=" * 60)
print("URL FEATURE EXTRACTION COMPLETED!")
print("=" * 60)

print("\nOriginal Dataset:")

print(
    f"{len(df):,} URLs"
)

print("\nFeatures Created:")

print(
    len(features_df.columns) - 1
)

print("\nOutput File:")

print(
    "dataSets/url_features.csv"
)

print("\nReady for URL model training!")