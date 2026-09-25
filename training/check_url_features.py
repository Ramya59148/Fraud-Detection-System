import os
import pandas as pd

# Import feature extraction from predict_url.py
from predict_url import extract_features

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Load feature order used during training
feature_file = os.path.join(
    BASE_DIR,
    "training",
    "saved_models",
    "url_model",
    "feature_names.txt"
)

with open(feature_file, "r", encoding="utf-8") as f:
    feature_names = [line.strip() for line in f if line.strip()]

# Test URL
url = "https://www.google.com"

# Extract live features
features = extract_features(url)
live_df = pd.DataFrame([features])

# Arrange columns exactly like training
live_df = live_df[feature_names]

print("="*60)
print("LIVE FEATURES FOR GOOGLE")
print("="*60)
print(live_df.T)

print("\nTotal Features:", len(live_df.columns))