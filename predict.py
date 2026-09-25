# ==========================================
# SENTRIX - COMBINED AI DETECTOR
# ==========================================

import os
import joblib
import pandas as pd
import torch

from urllib.parse import urlparse

from transformers import (
    DistilBertTokenizer,
    DistilBertForSequenceClassification
)


# ==========================================
# 1. PATHS
# ==========================================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

EMAIL_MODEL_PATH = os.path.join(
    BASE_DIR,
    "training",
    "saved_models",
    "email_model"
)

URL_MODEL_PATH = os.path.join(
    BASE_DIR,
    "training",
    "saved_models",
    "url_model"
)


# ==========================================
# 2. DEVICE
# ==========================================

device = torch.device(
    "cuda" if torch.cuda.is_available() else "cpu"
)

print("Using Device:", device)


# ==========================================
# 3. CHECK MODEL DIRECTORIES
# ==========================================

if not os.path.exists(EMAIL_MODEL_PATH):
    print("\nERROR: Email model not found!")
    print(EMAIL_MODEL_PATH)
    exit()

if not os.path.exists(URL_MODEL_PATH):
    print("\nERROR: URL model not found!")
    print(URL_MODEL_PATH)
    exit()


# ==========================================
# 4. LOAD EMAIL TOKENIZER
# ==========================================

print("\nLoading Email tokenizer...")

try:

    email_tokenizer = DistilBertTokenizer.from_pretrained(
        EMAIL_MODEL_PATH,
        local_files_only=True
    )

    print("Email tokenizer loaded successfully!")

except Exception as e:

    print("\nERROR loading Email tokenizer:")
    print(e)
    exit()


# ==========================================
# 5. LOAD EMAIL MODEL
# ==========================================

print("\nLoading Email model...")

try:

    email_model = DistilBertForSequenceClassification.from_pretrained(
        EMAIL_MODEL_PATH,
        local_files_only=True
    )

    email_model.to(device)
    email_model.eval()

    print("Email model loaded successfully!")

except Exception as e:

    print("\nERROR loading Email model:")
    print(e)
    exit()


# ==========================================
# 6. EMAIL LABEL MAPPING
# ==========================================

email_label_mapping = {
    0: "Critical",
    1: "Safe"
}

print("\nEmail Label Mapping:")
print(email_label_mapping)


# ==========================================
# 7. LOAD URL RANDOM FOREST MODEL
# ==========================================

print("\nLoading URL model...")

url_model_file = os.path.join(
    URL_MODEL_PATH,
    "url_random_forest.pkl"
)

if not os.path.exists(url_model_file):

    print("\nERROR: URL model file not found!")

    print(url_model_file)

    exit()


try:

    url_model = joblib.load(
        url_model_file
    )

    print("URL model loaded successfully!")

except Exception as e:

    print("\nERROR loading URL model:")
    print(e)

    print(
        "\nMake sure the model was saved using joblib.dump()."
    )

    exit()


# ==========================================
# 8. LOAD URL LABEL ENCODER
# ==========================================

print("\nLoading URL label encoder...")

encoder_file = os.path.join(
    URL_MODEL_PATH,
    "label_encoder.pkl"
)

if not os.path.exists(encoder_file):

    print("\nERROR: Label encoder not found!")

    print(encoder_file)

    exit()


try:

    url_encoder = joblib.load(
        encoder_file
    )

    print("URL label encoder loaded successfully!")

except Exception as e:

    print("\nERROR loading URL label encoder:")
    print(e)

    exit()


# ==========================================
# 9. LOAD FEATURE NAMES
# ==========================================

print("\nLoading URL feature names...")

feature_file = os.path.join(
    URL_MODEL_PATH,
    "feature_names.txt"
)

if not os.path.exists(feature_file):

    print("\nERROR: feature_names.txt not found!")

    exit()


with open(
    feature_file,
    "r",
    encoding="utf-8"
) as file:

    url_features = [
        line.strip()
        for line in file.readlines()
        if line.strip()
    ]


print(
    "URL features loaded:",
    len(url_features)
)


# ==========================================
# 10. URL FEATURE EXTRACTION
# ==========================================

def extract_url_features(url):

    url = str(url).strip()

    # ------------------------------
    # Make URL parseable
    # ------------------------------

    parse_target = url

    if not url.lower().startswith(
        ("http://", "https://")
    ):

        parse_target = "http://" + url

    try:

        parsed = urlparse(
            parse_target
        )

    except ValueError:

        parsed = urlparse(
            "http://invalid.local"
        )


    # ------------------------------
    # URL components
    # ------------------------------

    hostname = parsed.hostname or ""

    path = parsed.path or ""

    query = parsed.query or ""


    # ------------------------------
    # Feature dictionary
    # ------------------------------

    features = {}


    # Basic features

    features["url_length"] = len(url)

    features["hostname_length"] = len(
        hostname
    )

    features["path_length"] = len(
        path
    )

    features["query_length"] = len(
        query
    )


    # Character counts

    features["num_dots"] = url.count(
        "."
    )

    features["num_hyphens"] = url.count(
        "-"
    )

    features["num_underscores"] = url.count(
        "_"
    )

    features["num_slashes"] = url.count(
        "/"
    )

    features["num_question_marks"] = url.count(
        "?"
    )

    features["num_equals"] = url.count(
        "="
    )

    features["num_ampersands"] = url.count(
        "&"
    )

    features["num_at_symbols"] = url.count(
        "@"
    )

    features["num_percent_symbols"] = url.count(
        "%"
    )

    features["num_colons"] = url.count(
        ":"
    )


    # Digits

    features["num_digits"] = sum(
        character.isdigit()
        for character in url
    )


    # Letters

    features["num_letters"] = sum(
        character.isalpha()
        for character in url
    )


    # ------------------------------
    # Protocol
    # ------------------------------

    features["https"] = int(
        url.lower().startswith(
            "https"
        )
    )

    features["http"] = int(
        url.lower().startswith(
            "http"
        )
    )


    # ------------------------------
    # IP address
    # ------------------------------

    ip_address = 0

    try:

        parts = hostname.split(".")

        if (
            len(parts) == 4
            and all(
                part.isdigit()
                for part in parts
            )
        ):

            ip_address = 1

    except Exception:

        ip_address = 0


    features["ip_address"] = ip_address


    # ------------------------------
    # Subdomain
    # ------------------------------

    if hostname:

        features["subdomain_count"] = max(
            len(
                hostname.split(".")
            ) - 2,
            0
        )

    else:

        features["subdomain_count"] = 0


    # ------------------------------
    # Port
    # ------------------------------

    try:

        features["has_port"] = int(
            parsed.port is not None
        )

    except ValueError:

        features["has_port"] = 0


    # ------------------------------
    # URL components
    # ------------------------------

    features["has_query"] = int(
        bool(parsed.query)
    )

    features["has_fragment"] = int(
        bool(parsed.fragment)
    )


    # ------------------------------
    # Suspicious keywords
    # ------------------------------

    lower_url = url.lower()


    features["has_login"] = int(
        "login" in lower_url
    )

    features["has_verify"] = int(
        "verify" in lower_url
    )

    features["has_account"] = int(
        "account" in lower_url
    )

    features["has_secure"] = int(
        "secure" in lower_url
    )

    features["has_update"] = int(
        "update" in lower_url
    )

    features["has_password"] = int(
        "password" in lower_url
    )

    features["has_bank"] = int(
        "bank" in lower_url
    )

    features["has_free"] = int(
        "free" in lower_url
    )

    features["has_bonus"] = int(
        "bonus" in lower_url
    )

    features["has_confirm"] = int(
        "confirm" in lower_url
    )

    features["has_payment"] = int(
        "payment" in lower_url
    )

    features["has_wallet"] = int(
        "wallet" in lower_url
    )

    features["has_auth"] = int(
        "auth" in lower_url
    )


    # ------------------------------
    # Return EXACT training order
    # ------------------------------

    return [
        features.get(
            feature,
            0
        )
        for feature in url_features
    ]


# ==========================================
# 11. EMAIL PREDICTION
# ==========================================

def predict_email(text):

    inputs = email_tokenizer(
        text,
        return_tensors="pt",
        truncation=True,
        padding=True,
        max_length=128
    )


    inputs = {
        key: value.to(device)
        for key, value in inputs.items()
    }


    with torch.no_grad():

        outputs = email_model(
            **inputs
        )


        probabilities = torch.softmax(
            outputs.logits,
            dim=1
        )


        prediction = torch.argmax(
            probabilities,
            dim=1
        ).item()


    label = email_label_mapping.get(
        prediction,
        str(prediction)
    )


    confidence = probabilities[
        0,
        prediction
    ].item()


    return label, confidence


# ==========================================
# 12. URL PREDICTION
# ==========================================

def predict_url(url):

    features = extract_url_features(
        url
    )


    data = pd.DataFrame(
        [features],
        columns=url_features
    )


    prediction = url_model.predict(
        data
    )[0]


    probabilities = url_model.predict_proba(
        data
    )[0]


    label = url_encoder.inverse_transform(
        [prediction]
    )[0]


    confidence = max(
        probabilities
    )


    return label, confidence


# ==========================================
# 13. FINAL SENTRIX DECISION
# ==========================================

def final_decision(
    email_label,
    url_label
):

    if (
        email_label == "Critical"
        or
        url_label == "Critical"
    ):

        return "Critical"


    if (
        email_label == "Suspicious"
        or
        url_label == "Suspicious"
    ):

        return "Suspicious"


    return "Safe"


# ==========================================
# 14. START SENTRIX
# ==========================================

print("\n")

print("=" * 60)

print(
    "SENTRIX - COMBINED AI DETECTOR"
)

print("=" * 60)


print("\nModels loaded successfully!")

print("\nEmail Model: READY")

print("URL Model  : READY")

print("\nType 'exit' to close.")


# ==========================================
# 15. MAIN LOOP
# ==========================================

while True:

    print("\n")

    print("-" * 60)


    # ------------------------------
    # Email input
    # ------------------------------

    email_text = input(
        "\nEnter Email / Message: "
    )


    if email_text.lower().strip() == "exit":

        print(
            "\nSentrix closed."
        )

        break


    # ------------------------------
    # URL input
    # ------------------------------

    url = input(
        "Enter URL: "
    )


    if url.lower().strip() == "exit":

        print(
            "\nSentrix closed."
        )

        break


    # ------------------------------
    # Email prediction
    # ------------------------------

    try:

        email_label, email_confidence = predict_email(
            email_text
        )

    except Exception as e:

        print(
            "\nEmail prediction error:"
        )

        print(e)

        continue


    # ------------------------------
    # URL prediction
    # ------------------------------

    try:

        url_label, url_confidence = predict_url(
            url
        )

    except Exception as e:

        print(
            "\nURL prediction error:"
        )

        print(e)

        continue


    # ------------------------------
    # Final decision
    # ------------------------------

    final_label = final_decision(
        email_label,
        url_label
    )


    # ======================================
    # DISPLAY RESULT
    # ======================================

    print("\n")

    print("=" * 60)

    print(
        "SENTRIX ANALYSIS RESULT"
    )

    print("=" * 60)


    print(
        f"\nEmail Prediction : "
        f"{email_label}"
    )


    print(
        f"Email Confidence : "
        f"{email_confidence * 100:.2f}%"
    )


    print(
        f"\nURL Prediction   : "
        f"{url_label}"
    )


    print(
        f"URL Confidence   : "
        f"{url_confidence * 100:.2f}%"
    )


    print("\n" + "-" * 60)


    print(
        f"FINAL SENTRIX RESULT : "
        f"{final_label}"
    )


    print("=" * 60)