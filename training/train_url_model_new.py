import os
import pandas as pd
import joblib

from sklearn.ensemble import RandomForestClassifier

from url_feature_extractor import FEATURE_NAMES


DATA_FILE = "dataSets/url_train_new.csv"
MODEL_DIR = "training/saved_models/url_model_new"

MODEL_FILE = os.path.join(MODEL_DIR, "url_random_forest.pkl")
MAPPING_FILE = os.path.join(MODEL_DIR, "label_mapping.pkl")
FEATURE_FILE = os.path.join(MODEL_DIR, "feature_names.txt")


os.makedirs(MODEL_DIR, exist_ok=True)


print("Loading training data...")
df = pd.read_csv(DATA_FILE)

X = df[FEATURE_NAMES]
y = df["label"]


print("Training rows:", len(df))
print("Feature count:", len(FEATURE_NAMES))

print("\nTraining labels:")
print(y.value_counts())


# Explicit SentriX label mapping
label_to_id = {
    "Safe": 0,
    "Critical": 1,
    "Suspicious": 2
}

id_to_label = {
    0: "Safe",
    1: "Critical",
    2: "Suspicious"
}


print("\nLabel mapping:")
for label, class_id in label_to_id.items():
    print(f"{class_id} -> {label}")


# Convert labels using our explicit mapping
y_encoded = y.map(label_to_id)

if y_encoded.isna().any():
    raise ValueError("Unexpected label found in training data.")

y_encoded = y_encoded.astype(int)


print("\nEncoded label counts:")
print(y_encoded.value_counts().sort_index())


print("\nTraining Random Forest...")

model = RandomForestClassifier(
    n_estimators=300,
    max_features="sqrt",
    random_state=42,
    n_jobs=-1,
    class_weight="balanced"
)

model.fit(X, y_encoded)


print("\nTraining complete.")


# Save model
joblib.dump(model, MODEL_FILE)

# Save explicit mapping
joblib.dump(
    {
        "label_to_id": label_to_id,
        "id_to_label": id_to_label
    },
    MAPPING_FILE
)

# Save feature order
with open(FEATURE_FILE, "w", encoding="utf-8") as f:
    for feature in FEATURE_NAMES:
        f.write(feature + "\n")


print("\nSaved files:")
print(MODEL_FILE)
print(MAPPING_FILE)
print(FEATURE_FILE)

print("\nModel classes:")
print(model.classes_)

print("\nExpected class mapping:")
for class_id in model.classes_:
    print(f"{class_id} -> {id_to_label[int(class_id)]}")
