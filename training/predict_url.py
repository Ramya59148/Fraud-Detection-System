import os
import re
import joblib
import pandas as pd
from urllib.parse import urlparse


# ============================================================
# PATHS
# ============================================================

BASE_DIR = os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))
)

MODEL_DIR = os.path.join(
    BASE_DIR,
    "training",
    "saved_models",
    "url_model"
)

MODEL_PATH = os.path.join(
    MODEL_DIR,
    "url_random_forest.pkl"
)

ENCODER_PATH = os.path.join(
    MODEL_DIR,
    "label_encoder.pkl"
)

FEATURE_PATH = os.path.join(
    MODEL_DIR,
    "feature_names.txt"
)


# ============================================================
# LOAD MODEL / ENCODER / FEATURES
# ============================================================

print("Loading URL model...")

model = joblib.load(MODEL_PATH)
encoder = joblib.load(ENCODER_PATH)

with open(FEATURE_PATH, "r") as f:
    feature_names = [
        line.strip()
        for line in f
        if line.strip()
    ]

print("URL model loaded successfully.")


# ============================================================
# SHOW MODEL MAPPING
# ============================================================

print("\n========== MODEL INFORMATION ==========")

print("Model classes:")
print(model.classes_)

print("\nEncoder classes:")
print(encoder.classes_)

print("\nFeature count:")
print(len(feature_names))

print("\nFeature names:")
for i, name in enumerate(feature_names):
    print(f"{i}: {name}")

print("=======================================\n")


# ============================================================
# FEATURE EXTRACTION
# ============================================================

def extract_features(url):

    # Add scheme if user does not provide one
    if not re.match(r"^[a-zA-Z]+://", url):
        url = "http://" + url

    parsed = urlparse(url)

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

        "num_question_marks": url.count("?"),

        "num_equals": url.count("="),

        "num_ampersands": url.count("&"),

        "num_at_symbols": url.count("@"),

        "num_percent_symbols": url.count("%"),

        "num_digits": sum(
            c.isdigit()
            for c in url
        ),

        "num_letters": sum(
            c.isalpha()
            for c in url
        ),

        "https": int(
            parsed.scheme.lower() == "https"
        ),

        "ip_address": int(
            re.match(
                r"^(?:\d{1,3}\.){3}\d{1,3}$",
                hostname
            ) is not None
        ),

        "subdomain_count": max(
            0,
            len(hostname.split(".")) - 2
        ),

        "has_port": (
            int(parsed.port is not None)
            if parsed.hostname
            else 0
        ),

        "has_query": int(
            bool(parsed.query)
        ),

        "has_fragment": int(
            bool(parsed.fragment)
        ),

        "has_login": int(
            "login" in url.lower()
        ),

        "has_verify": int(
            "verify" in url.lower()
        ),

        "has_account": int(
            "account" in url.lower()
        ),

        "has_secure": int(
            "secure" in url.lower()
        ),

        "has_update": int(
            "update" in url.lower()
        ),

        "has_password": int(
            "password" in url.lower()
        ),

        "has_bank": int(
            "bank" in url.lower()
        ),

        "has_free": int(
            "free" in url.lower()
        ),

        "has_bonus": int(
            "bonus" in url.lower()
        ),

        "has_confirm": int(
            "confirm" in url.lower()
        ),

        "has_payment": int(
            "payment" in url.lower()
        ),

        "has_wallet": int(
            "wallet" in url.lower()
        ),

        "has_auth": int(
            "auth" in url.lower()
        )
    }

    # IMPORTANT:
    # Return features in the exact order used during training.
    return [
        features[name]
        for name in feature_names
    ]


# ============================================================
# URL PREDICTION
# ============================================================

print("=" * 55)
print("          SENTRIX - URL DETECTION")
print("=" * 55)


while True:

    url = input("\nEnter URL (or type exit): ").strip()

    if url.lower() == "exit":
        print("Program stopped.")
        break

    if not url:
        print("Please enter a URL.")
        continue

    try:

        # ----------------------------------------------------
        # Extract features
        # ----------------------------------------------------

        features = extract_features(url)

        X = pd.DataFrame(
            [features],
            columns=feature_names
        )

        # ----------------------------------------------------
        # DEBUG: INPUT
        # ----------------------------------------------------

        print("\n========== URL DEBUG ==========")

        print("Original URL:")
        print(url)

        print("\nFeatures:")
        print(X.to_string(index=False))

        # ----------------------------------------------------
        # MODEL PREDICTION
        # ----------------------------------------------------

        prediction = model.predict(X)[0]

        probabilities = model.predict_proba(X)[0]

        # Find the position of the predicted class
        predicted_index = list(
            model.classes_
        ).index(prediction)

        confidence = (
            probabilities[predicted_index] * 100
        )

        # Decode numerical class using the saved encoder
        label = encoder.inverse_transform(
            [prediction]
        )[0]

        # ----------------------------------------------------
        # DEBUG: MODEL OUTPUT
        # ----------------------------------------------------

        print("\nModel classes:")
        print(model.classes_)

        print("\nEncoder classes:")
        print(encoder.classes_)

        print("\nRaw prediction:")
        print(prediction)

        print("\nProbabilities:")

        for class_value, probability in zip(
            model.classes_,
            probabilities
        ):
            try:
                class_label = encoder.inverse_transform(
                    [class_value]
                )[0]
            except Exception:
                class_label = "UNKNOWN"

            print(
                f"Class {class_value} "
                f"({class_label}): "
                f"{probability * 100:.2f}%"
            )

        print("\nPredicted index:")
        print(predicted_index)

        print("\nFinal decoded label:")
        print(label)

        print("\nConfidence:")
        print(f"{confidence:.2f}%")

        print("================================")

        # ----------------------------------------------------
        # CURRENT RESULT
        # ----------------------------------------------------

        print("\n--------------------------------------")
        print("URL        :", url)
        print("Prediction :", label)
        print("Confidence :", f"{confidence:.2f}%")
        print("--------------------------------------")

    except Exception as e:

        print("\nERROR:")
        print(type(e).__name__, "-", e)