# ==========================================
# SENTRIX - EMAIL MODEL TRAINING
# ==========================================

# ==========================================
# 1. IMPORT LIBRARIES
# ==========================================

import os
import pandas as pd

from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder

from transformers import DistilBertTokenizer

from dataset import TextDataset

from trainer import (
    create_dataloaders,
    load_model,
    create_optimizer,
    train_model,
    evaluate_model,
    save_model,
    device
)


# ==========================================
# 2. DEFINE PROJECT PATHS
# ==========================================

# Current file:
# Sentrix/training/train_email.py
#
# Project root:
# Sentrix/

PROJECT_ROOT = os.path.dirname(
    os.path.dirname(
        os.path.abspath(__file__)
    )
)

DATASET_PATH = os.path.join(
    PROJECT_ROOT,
    "dataSets",
    "clean_email_dataset.csv"
)

MODEL_PATH = os.path.join(
    PROJECT_ROOT,
    "saved_models",
    "email_model"
)


# ==========================================
# 3. LOAD CLEANED EMAIL DATASET
# ==========================================

print("=" * 60)
print("SENTRIX - EMAIL MODEL TRAINING")
print("=" * 60)

print("\nLoading dataset...")
print("Dataset path:", DATASET_PATH)

df = pd.read_csv(DATASET_PATH)

print("\nDataset Loaded Successfully!")

print("\nFirst 5 Rows:")
print(df.head())

print("\nDataset Shape:")
print(df.shape)

print("\nColumns:")
print(df.columns)

print("\nMissing Values:")
print(df.isnull().sum())


# ==========================================
# 4. CHECK REQUIRED COLUMNS
# ==========================================

required_columns = ["text", "label"]

for column in required_columns:

    if column not in df.columns:

        raise ValueError(
            f"Required column '{column}' not found in dataset."
        )


# ==========================================
# 5. REMOVE EMPTY VALUES
# ==========================================

df = df.dropna(
    subset=["text", "label"]
)

# Remove completely empty text
df["text"] = df["text"].astype(str).str.strip()

df = df[df["text"] != ""]

print("\nAfter Cleaning:")
print(df.shape)


# ==========================================
# 6. CHECK ORIGINAL LABELS
# ==========================================

print("\nOriginal Labels:")
print(df["label"].value_counts())


# ==========================================
# 7. LABEL ENCODING
# ==========================================

encoder = LabelEncoder()

df["label"] = encoder.fit_transform(
    df["label"]
)


print("\nEncoded Labels:")
print(df["label"].value_counts())


# ==========================================
# 8. DISPLAY LABEL MAPPING
# ==========================================

print("\nLabel Mapping:")

for number, label in enumerate(
    encoder.classes_
):

    print(
        f"{number} -> {label}"
    )


# ==========================================
# 9. NUMBER OF CLASSES
# ==========================================

num_labels = len(
    encoder.classes_
)

print(
    "\nNumber of Classes:",
    num_labels
)


# ==========================================
# 10. TRAIN / TEST SPLIT
# ==========================================

X_train, X_test, y_train, y_test = train_test_split(

    df["text"],

    df["label"],

    test_size=0.2,

    random_state=42,

    stratify=df["label"]
)


print(
    "\nTraining Samples:",
    len(X_train)
)

print(
    "Testing Samples:",
    len(X_test)
)


# ==========================================
# 11. LOAD DISTILBERT TOKENIZER
# ==========================================

print(
    "\nLoading DistilBERT Tokenizer..."
)

tokenizer = DistilBertTokenizer.from_pretrained(
    "distilbert-base-uncased"
)

print(
    "Tokenizer Loaded Successfully!"
)


# ==========================================
# 12. TEST TOKENIZATION
# ==========================================

sample = X_train.iloc[0]

print("\n" + "-" * 50)

print("SAMPLE EMAIL")

print("-" * 50)

print(sample)


tokens = tokenizer(

    sample,

    truncation=True,

    padding="max_length",

    max_length=128
)


print("\n" + "-" * 50)

print("TOKENIZED OUTPUT")

print("-" * 50)

print(tokens)


# ==========================================
# 13. CREATE TRAINING DATASET
# ==========================================

train_dataset = TextDataset(

    X_train,

    y_train,

    tokenizer
)


# ==========================================
# 14. CREATE TEST DATASET
# ==========================================

test_dataset = TextDataset(

    X_test,

    y_test,

    tokenizer
)


print("\n" + "-" * 50)

print("DATASET OBJECTS CREATED")

print("-" * 50)

print(
    "Training Dataset Size:",
    len(train_dataset)
)

print(
    "Testing Dataset Size:",
    len(test_dataset)
)


# ==========================================
# 15. CREATE DATALOADERS
# ==========================================

train_loader, test_loader = create_dataloaders(

    train_dataset,

    test_dataset,

    batch_size=16
)


print(
    "\nDataLoaders Created Successfully!"
)


# ==========================================
# 16. LOAD DISTILBERT MODEL
# ==========================================

print(
    "\nLoading DistilBERT Model..."
)

model = load_model(

    num_labels=num_labels
)

print(
    "DistilBERT Model Loaded Successfully!"
)


# ==========================================
# 17. CREATE OPTIMIZER
# ==========================================

optimizer = create_optimizer(
    model
)

print(
    "Optimizer Created Successfully!"
)


# ==========================================
# 18. DISPLAY DEVICE
# ==========================================

print(
    "\nTraining Device:",
    device
)


# ==========================================
# 19. START TRAINING
# ==========================================

print("\n")

print("=" * 60)

print(
    "STARTING EMAIL MODEL TRAINING"
)

print("=" * 60)


train_model(

    model=model,

    train_loader=train_loader,

    optimizer=optimizer,

    device=device,

    epochs=3
)


# ==========================================
# 20. EVALUATE MODEL
# ==========================================

print("\n")

print("=" * 60)

print(
    "EVALUATING EMAIL MODEL"
)

print("=" * 60)


accuracy = evaluate_model(

    model,

    test_loader,

    device
)


print(
    "\nFinal Email Model Accuracy:"
)

print(
    f"{accuracy * 100:.2f}%"
)


# ==========================================
# 21. CREATE MODEL DIRECTORY
# ==========================================

os.makedirs(

    MODEL_PATH,

    exist_ok=True
)


print(
    "\nModel directory created:"
)

print(MODEL_PATH)


# ==========================================
# 22. SAVE TRAINED MODEL
# ==========================================

print(
    "\nSaving trained model..."
)

save_model(

    model,

    MODEL_PATH
)


# ==========================================
# 23. SAVE TOKENIZER
# ==========================================

print(
    "\nSaving tokenizer..."
)

tokenizer.save_pretrained(
    MODEL_PATH
)

print(
    "Tokenizer Saved Successfully!"
)


# ==========================================
# 24. SAVE LABEL MAPPING
# ==========================================

print(
    "\nSaving label mapping..."
)


label_mapping = {

    str(number): label

    for number, label in enumerate(
        encoder.classes_
    )

}


mapping_df = pd.DataFrame(

    list(label_mapping.items()),

    columns=[
        "id",
        "label"
    ]

)


mapping_path = os.path.join(

    MODEL_PATH,

    "label_mapping.csv"
)


mapping_df.to_csv(

    mapping_path,

    index=False
)


print(
    "Label Mapping Saved Successfully!"
)


# ==========================================
# 25. DISPLAY SAVED FILES
# ==========================================

print("\n")

print("=" * 60)

print(
    "SAVED MODEL FILES"
)

print("=" * 60)


for file in os.listdir(MODEL_PATH):

    print(
        " -",
        file
    )


# ==========================================
# 26. FINAL MESSAGE
# ==========================================

print("\n")

print("=" * 60)

print(
    "EMAIL MODEL TRAINING COMPLETED SUCCESSFULLY!"
)

print("=" * 60)


print(
    "\nModel Location:"
)

print(
    MODEL_PATH
)


print(
    "\nFinal Accuracy:"
)

print(
    f"{accuracy * 100:.2f}%"
)


print(
    "\nSentrix Email AI Model is Ready!"
)