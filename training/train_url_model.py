# ==========================================
# SENTRIX - URL ML MODEL TRAINING
# ==========================================

import os
import joblib
import numpy as np
import pandas as pd

from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix
)


# ==========================================
# 1. PATHS
# ==========================================

BASE_DIR = os.path.dirname(
    os.path.dirname(
        os.path.abspath(__file__)
    )
)

DATA_FILE = os.path.join(
    BASE_DIR,
    "dataSets",
    "url_features.csv"
)

MODEL_DIR = os.path.join(
    BASE_DIR,
    "training",
    "saved_models",
    "url_model"
)

MODEL_FILE = os.path.join(
    MODEL_DIR,
    "url_random_forest.pkl"
)

ENCODER_FILE = os.path.join(
    MODEL_DIR,
    "label_encoder.pkl"
)

FEATURE_FILE = os.path.join(
    MODEL_DIR,
    "feature_names.txt"
)


# ==========================================
# 2. CREATE MODEL DIRECTORY
# ==========================================

os.makedirs(
    MODEL_DIR,
    exist_ok=True
)


# ==========================================
# 3. LOAD FEATURE DATASET
# ==========================================

print("=" * 60)
print("SENTRIX - URL ML MODEL TRAINING")
print("=" * 60)

print("\nLoading URL feature dataset...")

if not os.path.exists(DATA_FILE):

    raise FileNotFoundError(
        f"\nURL feature dataset not found:\n{DATA_FILE}"
    )

df = pd.read_csv(
    DATA_FILE
)

print("\nDataset Loaded Successfully!")

print("\nDataset Shape:")
print(df.shape)

print("\nColumns:")
print(df.columns.tolist())

print("\nMissing Values:")
print(df.isnull().sum().sum())


# ==========================================
# 4. CHECK LABEL COLUMN
# ==========================================

if "label" not in df.columns:

    raise ValueError(
        "ERROR: 'label' column not found!"
    )


# ==========================================
# 5. LABEL CLEANING
# ==========================================

df = df.dropna(
    subset=["label"]
).copy()

df["label"] = (
    df["label"]
    .astype(str)
    .str.strip()
)


print("\nDataset after cleaning:")
print(df.shape)


# ==========================================
# 6. ORIGINAL LABEL DISTRIBUTION
# ==========================================

print("\n")
print("=" * 60)
print("ORIGINAL LABEL DISTRIBUTION")
print("=" * 60)

print(
    df["label"].value_counts()
)


# ==========================================
# 7. CHECK EXPECTED LABELS
# ==========================================

expected_labels = {
    "Safe",
    "Critical",
    "Suspicious"
}

actual_labels = set(
    df["label"].unique()
)

print("\nLabels found in dataset:")

for label in sorted(actual_labels):

    print(
        "-",
        label
    )


unknown_labels = actual_labels - expected_labels

if unknown_labels:

    raise ValueError(
        "\nUnexpected labels found in dataset: "
        + str(unknown_labels)
        + "\nExpected only: Safe, Critical, Suspicious"
    )


missing_labels = expected_labels - actual_labels

if missing_labels:

    raise ValueError(
        "\nExpected labels missing from dataset: "
        + str(missing_labels)
    )


# ==========================================
# 8. SEPARATE FEATURES AND LABEL
# ==========================================

X = df.drop(
    columns=["label"]
)

y = df["label"]


print("\nNumber of Features:")
print(
    X.shape[1]
)


print("\nFeature Names:")

for feature in X.columns:

    print(
        "-",
        feature
    )


# ==========================================
# 9. CUSTOM LABEL MAPPING
# ==========================================

print("\n")
print("=" * 60)
print("CUSTOM LABEL MAPPING")
print("=" * 60)


label_mapping = {
    "Safe": 0,
    "Critical": 1,
    "Suspicious": 2
}


print("\nRequired Mapping:")

print("0 -> Safe")
print("1 -> Critical")
print("2 -> Suspicious")


# Convert text labels to our required numbers

y_encoded = y.map(
    label_mapping
)


# Check conversion

if y_encoded.isnull().any():

    raise ValueError(
        "\nSome labels could not be converted!"
    )


y_encoded = y_encoded.astype(int)


# ==========================================
# 10. CREATE LABEL ENCODER
# ==========================================

encoder = LabelEncoder()

# IMPORTANT:
# We manually set the classes in the required order.
#
# Normal LabelEncoder.fit() sorts alphabetically.
# We do NOT use fit() here.

encoder.classes_ = np.array(
    [
        "Safe",
        "Critical",
        "Suspicious"
    ],
    dtype=object
)


print("\n")
print("=" * 60)
print("FINAL LABEL ENCODING")
print("=" * 60)

for number, label in enumerate(
    encoder.classes_
):

    print(
        f"{number} -> {label}"
    )


# ==========================================
# 11. TRAIN / TEST SPLIT
# ==========================================

X_train, X_test, y_train, y_test = train_test_split(

    X,

    y_encoded,

    test_size=0.20,

    random_state=42,

    stratify=y_encoded
)


print("\n")
print("=" * 60)
print("TRAIN / TEST SPLIT")
print("=" * 60)

print(
    "\nTraining Samples:",
    len(X_train)
)

print(
    "Testing Samples:",
    len(X_test)
)


# ==========================================
# 12. CREATE RANDOM FOREST
# ==========================================

print("\n")
print("=" * 60)
print("CREATING RANDOM FOREST MODEL")
print("=" * 60)


model = RandomForestClassifier(

    n_estimators=200,

    max_depth=None,

    random_state=42,

    n_jobs=-1,

    class_weight="balanced"
)


print("\nRandom Forest Configuration:")

print(
    "Number of Trees:",
    200
)

print(
    "Class Weight:",
    "balanced"
)

print(
    "CPU Threads:",
    "All available"
)


# ==========================================
# 13. TRAIN MODEL
# ==========================================

print("\n")
print("=" * 60)
print("STARTING URL MODEL TRAINING")
print("=" * 60)

print("\nPlease wait...")

print(
    f"{len(df):,} URLs are being processed."
)


model.fit(
    X_train,
    y_train
)


print("\n")
print("=" * 60)
print("URL MODEL TRAINING COMPLETED!")
print("=" * 60)


# ==========================================
# 14. MODEL CLASSES
# ==========================================

print("\nModel Classes:")

print(
    model.classes_
)


# ==========================================
# 15. MAKE PREDICTIONS
# ==========================================

print("\nMaking predictions...")

y_pred = model.predict(
    X_test
)


# ==========================================
# 16. CALCULATE ACCURACY
# ==========================================

accuracy = accuracy_score(
    y_test,
    y_pred
)


print("\n")
print("=" * 60)
print("MODEL PERFORMANCE")
print("=" * 60)

print(
    f"\nAccuracy: {accuracy * 100:.2f}%"
)


# ==========================================
# 17. CLASSIFICATION REPORT
# ==========================================

print("\nClassification Report:")

print(
    classification_report(
        y_test,
        y_pred,
        labels=[0, 1, 2],
        target_names=[
            "Safe",
            "Critical",
            "Suspicious"
        ],
        zero_division=0
    )
)


# ==========================================
# 18. CONFUSION MATRIX
# ==========================================

print("\nConfusion Matrix:")

cm = confusion_matrix(
    y_test,
    y_pred,
    labels=[0, 1, 2]
)

print(cm)

print("\nConfusion Matrix Order:")

print(
    "0 = Safe"
)

print(
    "1 = Critical"
)

print(
    "2 = Suspicious"
)


# ==========================================
# 19. FEATURE IMPORTANCE
# ==========================================

print("\n")
print("=" * 60)
print("TOP URL FEATURES")
print("=" * 60)


feature_importance = pd.DataFrame({

    "feature": X.columns,

    "importance":
        model.feature_importances_

})


feature_importance = (
    feature_importance
    .sort_values(
        by="importance",
        ascending=False
    )
)


print(
    feature_importance.head(15)
)


# ==========================================
# 20. SAVE RANDOM FOREST MODEL
# ==========================================

print("\n")
print("=" * 60)
print("SAVING URL MODEL")
print("=" * 60)


joblib.dump(
    model,
    MODEL_FILE
)


print(
    "\nRandom Forest model saved:"
)

print(
    MODEL_FILE
)


# ==========================================
# 21. SAVE LABEL ENCODER
# ==========================================

joblib.dump(
    encoder,
    ENCODER_FILE
)


print(
    "\nLabel encoder saved:"
)

print(
    ENCODER_FILE
)


# ==========================================
# 22. SAVE FEATURE NAMES
# ==========================================

with open(
    FEATURE_FILE,
    "w",
    encoding="utf-8"
) as file:

    for feature in X.columns:

        file.write(
            feature + "\n"
        )


print(
    "\nFeature names saved:"
)

print(
    FEATURE_FILE
)


# ==========================================
# 23. FINAL MESSAGE
# ==========================================

print("\n")
print("=" * 60)
print("SENTRIX URL MODEL READY!")
print("=" * 60)

print("\nModel Location:")

print(
    MODEL_DIR
)

print("\nFiles Created:")

print(
    "1. url_random_forest.pkl"
)

print(
    "2. label_encoder.pkl"
)

print(
    "3. feature_names.txt"
)

print("\nFinal Accuracy:")

print(
    f"{accuracy * 100:.2f}%"
)

print("\nFinal Label Mapping:")

print(
    "0 -> Safe"
)

print(
    "1 -> Critical"
)

print(
    "2 -> Suspicious"
)

print("\nURL AI training completed successfully!")