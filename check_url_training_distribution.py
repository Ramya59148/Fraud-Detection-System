import pandas as pd
import joblib
import os

DATASET = "./dataSets/url_features.csv"
MODEL_DIR = "./training/saved_models/url_model"

df = pd.read_csv(DATASET)

model = joblib.load(
    os.path.join(MODEL_DIR, "url_random_forest.pkl")
)

with open(os.path.join(MODEL_DIR, "feature_names.txt"), "r") as f:
    feature_names = [x.strip() for x in f if x.strip()]

print("\nDataset shape:", df.shape)

print("\nLABEL COUNTS")
print(df["label"].value_counts())

# Google feature vector from our previous test
google = {
    "url_length": 22,
    "hostname_length": 14,
    "path_length": 0,
    "query_length": 0,
    "num_dots": 2,
    "num_hyphens": 0,
    "num_underscores": 0,
    "num_slashes": 2,
    "num_question_marks": 0,
    "num_equals": 0,
    "num_ampersands": 0,
    "num_at_symbols": 0,
    "num_percent_symbols": 0,
    "num_colons": 1,
    "num_digits": 0,
    "num_letters": 17,
    "https": 1,
    "http": 0,
    "ip_address": 0,
    "subdomain_count": 1,
    "has_port": 0,
    "has_query": 0,
    "has_fragment": 0,
    "has_login": 0,
    "has_verify": 0,
    "has_account": 0,
    "has_secure": 0,
    "has_update": 0,
    "has_password": 0,
    "has_bank": 0,
    "has_free": 0,
    "has_bonus": 0,
    "has_confirm": 0,
    "has_payment": 0,
    "has_wallet": 0,
    "has_auth": 0,
}

print("\nGOOGLE FEATURE VECTOR")
for feature in feature_names:
    print(f"{feature:25} = {google[feature]}")

# Find training rows with exactly the same feature vector
mask = pd.Series(True, index=df.index)

for feature in feature_names:
    mask &= df[feature] == google[feature]

matches = df[mask]

print("\n" + "=" * 70)
print("EXACT FEATURE MATCHES")
print("=" * 70)

print("Number of matching training rows:", len(matches))

if len(matches) > 0:
    print("\nLabels of exact matches:")
    print(matches["label"].value_counts())

    print("\nMatching rows:")
    print(matches[["label"]].head(20).to_string(index=False))

# Find rows closest to Google's feature vector
numeric = df[feature_names].copy()

google_vector = pd.Series(google)[feature_names]

# Normalize each feature so large-valued features don't dominate
mins = numeric.min()
maxs = numeric.max()

ranges = (maxs - mins).replace(0, 1)

normalized = (numeric - mins) / ranges
google_normalized = (google_vector - mins) / ranges

distance = ((normalized - google_normalized) ** 2).sum(axis=1) ** 0.5

closest_indices = distance.nsmallest(20).index

closest = df.loc[closest_indices, ["label"]].copy()
closest["distance"] = distance.loc[closest_indices]

print("\n" + "=" * 70)
print("20 CLOSEST TRAINING EXAMPLES")
print("=" * 70)

print(closest.sort_values("distance").to_string(index=False))

print("\n" + "=" * 70)
print("CLOSEST EXAMPLE URLS")
print("=" * 70)

if "url" in df.columns:
    output = df.loc[closest_indices, ["url", "label"]].copy()
    output["distance"] = distance.loc[closest_indices]
    print(output.sort_values("distance").to_string(index=False))
else:
    print("url column is not present in url_features.csv")