# ==========================================
# SENTRIX - URL MODEL EVALUATION
# ==========================================

import pandas as pd
import joblib

from sklearn.model_selection import train_test_split
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    classification_report,
    confusion_matrix
)

# ==========================================
# 1. PATHS
# ==========================================

DATASET_PATH = "dataSets/url_features.csv"

MODEL_PATH = "training/saved_models/url_model/url_random_forest.pkl"

ENCODER_PATH = "training/saved_models/url_model/label_encoder.pkl"

FEATURE_PATH = "training/saved_models/url_model/feature_names.txt"


# ==========================================
# 2. LOAD DATASET
# ==========================================

print("=" * 60)
print("SENTRIX - URL MODEL EVALUATION")
print("=" * 60)

print("\nLoading dataset...")

df = pd.read_csv(DATASET_PATH)

print("Dataset loaded successfully!")

print("\nDataset Shape:")
print(df.shape)


# ==========================================
# 3. LOAD MODEL
# ==========================================

print("\nLoading trained Random Forest model...")

model = joblib.load(MODEL_PATH)

print("Model loaded successfully!")


# ==========================================
# 4. LOAD LABEL ENCODER
# ==========================================

print("\nLoading label encoder...")

encoder = joblib.load(ENCODER_PATH)

print("Label encoder loaded successfully!")

print("\nLabel Mapping:")

for number, label in enumerate(encoder.classes_):
    print(f"{number} -> {label}")


# ==========================================
# 5. LOAD FEATURE NAMES
# ==========================================

print("\nLoading feature names...")

with open(FEATURE_PATH, "r") as f:
    feature_names = [line.strip() for line in f.readlines()]

print("Number of features:", len(feature_names))


# ==========================================
# 6. PREPARE X AND Y
# ==========================================

X = df[feature_names]

y = encoder.transform(df["label"])


print("\nFeatures Shape:")
print(X.shape)

print("\nLabels Shape:")
print(y.shape)


# ==========================================
# 7. SAME TEST SPLIT
# ==========================================

X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.2,
    random_state=42,
    stratify=y
)

print("\nTraining Samples:", len(X_train))
print("Testing Samples :", len(X_test))


# ==========================================
# 8. PREDICTION
# ==========================================

print("\nGenerating predictions...")

y_pred = model.predict(X_test)

print("Prediction completed!")


# ==========================================
# 9. ACCURACY
# ==========================================

accuracy = accuracy_score(y_test, y_pred)

print("\n" + "=" * 60)
print("MODEL PERFORMANCE")
print("=" * 60)

print(f"\nAccuracy : {accuracy * 100:.2f}%")


# ==========================================
# 10. PRECISION
# ==========================================

precision = precision_score(
    y_test,
    y_pred,
    average="weighted",
    zero_division=0
)

print(f"Precision: {precision * 100:.2f}%")


# ==========================================
# 11. RECALL
# ==========================================

recall = recall_score(
    y_test,
    y_pred,
    average="weighted",
    zero_division=0
)

print(f"Recall   : {recall * 100:.2f}%")


# ==========================================
# 12. F1 SCORE
# ==========================================

f1 = f1_score(
    y_test,
    y_pred,
    average="weighted",
    zero_division=0
)

print(f"F1 Score : {f1 * 100:.2f}%")


# ==========================================
# 13. CLASSIFICATION REPORT
# ==========================================

print("\n" + "=" * 60)
print("CLASSIFICATION REPORT")
print("=" * 60)

print(
    classification_report(
        y_test,
        y_pred,
        target_names=encoder.classes_,
        zero_division=0
    )
)


# ==========================================
# 14. CONFUSION MATRIX
# ==========================================

print("=" * 60)
print("CONFUSION MATRIX")
print("=" * 60)

cm = confusion_matrix(y_test, y_pred)

print("\nLabels:")
print(list(encoder.classes_))

print("\nConfusion Matrix:")
print(cm)


# ==========================================
# 15. FINAL RESULT
# ==========================================

print("\n" + "=" * 60)
print("URL MODEL EVALUATION COMPLETED")
print("=" * 60)

print(f"""
Accuracy : {accuracy * 100:.2f}%
Precision: {precision * 100:.2f}%
Recall   : {recall * 100:.2f}%
F1 Score : {f1 * 100:.2f}%
""")