import joblib
import pandas as pd
import numpy as np
from urllib.parse import urlparse
import re
import os

MODEL_DIR = "./training/saved_models/url_model"

model = joblib.load(os.path.join(MODEL_DIR, "url_random_forest.pkl"))
encoder = joblib.load(os.path.join(MODEL_DIR, "label_encoder.pkl"))

with open(os.path.join(MODEL_DIR, "feature_names.txt"), "r") as f:
    feature_names = [line.strip() for line in f if line.strip()]


def extract_features(url):
    parsed = urlparse(url if "://" in url else "http://" + url)

    hostname = parsed.hostname or ""
    path = parsed.path or ""
    query = parsed.query or ""

    features = {
        "url_length": len(url),
        "hostname_length": len(hostname),
        "path_length": len(path),
        "query_length": len(query),
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

        "ip_address": int(
            bool(re.match(r"^\d{1,3}(\.\d{1,3}){3}$", hostname))
        ),

        "subdomain_count": max(0, len(hostname.split(".")) - 2),

        "has_port": int(parsed.port is not None),
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


def predict(url):
    features = extract_features(url)

    X = pd.DataFrame([features])

    # EXACT feature order used by the saved model
    X = X[feature_names]

    prediction = model.predict(X)[0]
    probabilities = model.predict_proba(X)[0]

    label = encoder.inverse_transform([prediction])[0]

    result = {
        "url": url,
        "prediction": label
    }

    for cls, prob in zip(model.classes_, probabilities):
        label_name = encoder.inverse_transform([cls])[0]
        result[label_name] = round(prob * 100, 4)

    return result, features


urls = [
    "https://www.google.com",
    "http://www.google.com",
    "google.com",
    "www.google.com",
    "en.wikipedia.org/wiki/North_Dakota",
]

for url in urls:
    result, features = predict(url)

    print("\n" + "=" * 60)
    print(url)
    print("=" * 60)

    print("Prediction :", result["prediction"])

    for label in ["Critical", "Suspicious", "Safe"]:
        if label in result:
            print(f"{label:11}: {result[label]:.4f}%")