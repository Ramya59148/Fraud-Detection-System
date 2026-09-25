# ==========================================
# SENTRIX - TEXT MODEL TRAINING
# ==========================================

import os
import json
import numpy as np
import pandas as pd
import torch

from torch.utils.data import Dataset
from sklearn.model_selection import train_test_split
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix
)

from transformers import (
    DistilBertTokenizer,
    DistilBertForSequenceClassification,
    Trainer,
    TrainingArguments
)


# ==========================================
# 1. PATHS
# ==========================================

BASE_DIR = os.path.dirname(
    os.path.dirname(
        os.path.abspath(__file__)
    )
)

DATASET_FILE = os.path.join(
    BASE_DIR,
    "dataSets",
    "clean_text_dataset.csv"
)

MODEL_DIR = os.path.join(
    BASE_DIR,
    "training",
    "saved_models",
    "text_model"
)


# ==========================================
# 2. SETTINGS
# ==========================================

SEED = 42

MAX_LENGTH = 128

NUM_LABELS = 2


# ==========================================
# 3. DEVICE
# ==========================================

device = torch.device(
    "cuda" if torch.cuda.is_available()
    else "cpu"
)


print("=" * 60)
print("SENTRIX - TEXT AI MODEL TRAINING")
print("=" * 60)

print("\nDevice:")
print(device)


# ==========================================
# 4. LOAD DATASET
# ==========================================

print("\nLoading dataset...")

df = pd.read_csv(
    DATASET_FILE
)

print("\nDataset Loaded Successfully!")

print("\nDataset Shape:")
print(df.shape)

print("\nColumns:")
print(df.columns.tolist())

print("\nMissing Values:")
print(df.isnull().sum())


# ==========================================
# 5. CHECK REQUIRED COLUMNS
# ==========================================

if "text" not in df.columns:

    raise ValueError(
        "ERROR: 'text' column not found!"
    )


if "label" not in df.columns:

    raise ValueError(
        "ERROR: 'label' column not found!"
    )


# ==========================================
# 6. REMOVE MISSING VALUES
# ==========================================

df = df.dropna(
    subset=[
        "text",
        "label"
    ]
).copy()


# ==========================================
# 7. CLEAN TEXT AND LABELS
# ==========================================

df["text"] = (
    df["text"]
    .astype(str)
    .str.strip()
)

df["label"] = (
    df["label"]
    .astype(str)
    .str.strip()
)


# Remove empty text

df = df[
    df["text"] != ""
].copy()


print("\nDataset after cleaning:")
print(df.shape)


# ==========================================
# 8. CHECK ORIGINAL LABELS
# ==========================================

print("\nOriginal Label Distribution:")

print(
    df["label"].value_counts()
)


# ==========================================
# 9. LABEL MAPPING
# ==========================================

label_mapping = {

    "Safe": 0,

    "Critical": 1

}


invalid_labels = set(
    df["label"].unique()
) - set(
    label_mapping.keys()
)


if invalid_labels:

    raise ValueError(
        f"Unexpected labels found: "
        f"{invalid_labels}"
    )


df["label_id"] = (
    df["label"]
    .map(label_mapping)
    .astype(int)
)


print("\nLabel Mapping:")

print("Safe     -> 0")
print("Critical -> 1")


# ==========================================
# 10. TRAIN TEST SPLIT
# ==========================================

X_train, X_test, y_train, y_test = train_test_split(

    df["text"],

    df["label_id"],

    test_size=0.20,

    random_state=SEED,

    stratify=df["label_id"]

)


print("\nTraining Samples:")
print(len(X_train))

print("\nTesting Samples:")
print(len(X_test))


# ==========================================
# 11. LOAD DISTILBERT TOKENIZER
# ==========================================

print("\nLoading DistilBERT tokenizer...")

tokenizer = DistilBertTokenizer.from_pretrained(

    "distilbert-base-uncased",

    local_files_only=True

)


print(
    "Tokenizer Loaded Successfully!"
)


# ==========================================
# 12. TEST TOKENIZER
# ==========================================

sample = X_train.iloc[0]


print("\nSample Text:")
print(sample)


tokens = tokenizer(
    sample
)


print("\nTokenized Output:")
print(tokens)


# ==========================================
# 13. CREATE DATASET CLASS
# ==========================================

class TextDataset(Dataset):

    def __init__(
        self,
        texts,
        labels,
        tokenizer,
        max_length=128
    ):

        self.texts = texts.tolist()

        self.labels = labels.tolist()

        self.tokenizer = tokenizer

        self.max_length = max_length


    def __len__(self):

        return len(self.texts)


    def __getitem__(self, idx):

        text = self.texts[idx]

        label = self.labels[idx]


        encoding = self.tokenizer(

            text,

            truncation=True,

            padding="max_length",

            max_length=self.max_length,

            return_tensors="pt"

        )


        return {

            "input_ids":
                encoding["input_ids"].squeeze(0),

            "attention_mask":
                encoding["attention_mask"].squeeze(0),

            "labels":
                torch.tensor(
                    label,
                    dtype=torch.long
                )

        }


# ==========================================
# 14. CREATE DATASETS
# ==========================================

train_dataset = TextDataset(

    X_train,

    y_train,

    tokenizer,

    MAX_LENGTH

)


test_dataset = TextDataset(

    X_test,

    y_test,

    tokenizer,

    MAX_LENGTH

)


print("\nTraining Dataset Size:")
print(len(train_dataset))


print("\nTesting Dataset Size:")
print(len(test_dataset))


# ==========================================
# 15. LOAD DISTILBERT CLASSIFIER
# ==========================================

print("\nLoading DistilBERT classification model...")


model = DistilBertForSequenceClassification.from_pretrained(

    "distilbert-base-uncased",

    num_labels=NUM_LABELS,

    local_files_only=True

)


print(
    "DistilBERT Classification Model Loaded!"
)


# ==========================================
# 16. MOVE MODEL TO DEVICE
# ==========================================

model.to(device)


# ==========================================
# 17. ID TO LABEL MAPPING
# ==========================================

id2label = {

    0: "Safe",

    1: "Critical"

}


label2id = {

    "Safe": 0,

    "Critical": 1

}


model.config.id2label = id2label

model.config.label2id = label2id


# ==========================================
# 18. METRICS
# ==========================================

def compute_metrics(eval_prediction):

    predictions = eval_prediction.predictions

    labels = eval_prediction.label_ids


    predicted_labels = np.argmax(

        predictions,

        axis=1

    )


    accuracy = accuracy_score(

        labels,

        predicted_labels

    )


    return {

        "accuracy": accuracy

    }


# ==========================================
# 19. TRAINING ARGUMENTS
# ==========================================

training_args = TrainingArguments(

    output_dir=MODEL_DIR,

    num_train_epochs=3,

    per_device_train_batch_size=8,

    per_device_eval_batch_size=8,

    learning_rate=2e-5,

    weight_decay=0.01,

    logging_steps=50,

    save_strategy="epoch",

    report_to="none",

    seed=SEED

)


# ==========================================
# 20. CREATE TRAINER
# ==========================================

trainer = Trainer(

    model=model,

    args=training_args,

    train_dataset=train_dataset,

    eval_dataset=test_dataset,

    compute_metrics=compute_metrics

)


# ==========================================
# 21. START TRAINING
# ==========================================

print("\n")
print("=" * 60)
print("STARTING DISTILBERT TRAINING")
print("=" * 60)


trainer.train()


# ==========================================
# 22. EVALUATE MODEL
# ==========================================

print("\n")
print("=" * 60)
print("EVALUATING TEXT MODEL")
print("=" * 60)


evaluation = trainer.evaluate()


print("\nEvaluation Results:")


for key, value in evaluation.items():

    print(
        f"{key}: {value}"
    )


# ==========================================
# 23. GENERATE PREDICTIONS
# ==========================================

print("\nGenerating predictions...")


prediction_output = trainer.predict(

    test_dataset

)


predictions = np.argmax(

    prediction_output.predictions,

    axis=1

)


true_labels = np.array(
    y_test
)


# ==========================================
# 24. ACCURACY
# ==========================================

accuracy = accuracy_score(

    true_labels,

    predictions

)


print("\n")
print("=" * 60)
print("TEXT MODEL ACCURACY")
print("=" * 60)


print(
    f"\nAccuracy: {accuracy * 100:.2f}%"
)


# ==========================================
# 25. CLASSIFICATION REPORT
# ==========================================

print("\n")
print("=" * 60)
print("CLASSIFICATION REPORT")
print("=" * 60)


report = classification_report(

    true_labels,

    predictions,

    target_names=[
        "Safe",
        "Critical"
    ]

)


print(report)


# ==========================================
# 26. CONFUSION MATRIX
# ==========================================

print("\n")
print("=" * 60)
print("CONFUSION MATRIX")
print("=" * 60)


cm = confusion_matrix(

    true_labels,

    predictions

)


print("\n")

print(cm)


# ==========================================
# 27. SAVE MODEL
# ==========================================

print("\n")
print("=" * 60)
print("SAVING TEXT MODEL")
print("=" * 60)


os.makedirs(

    MODEL_DIR,

    exist_ok=True

)


trainer.save_model(

    MODEL_DIR

)


# ==========================================
# 28. SAVE TOKENIZER
# ==========================================

tokenizer.save_pretrained(

    MODEL_DIR

)


# ==========================================
# 29. SAVE LABEL MAPPING
# ==========================================

mapping_file = os.path.join(

    MODEL_DIR,

    "label_mapping.json"

)


with open(

    mapping_file,

    "w",

    encoding="utf-8"

) as file:

    json.dump(

        {
            "0": "Safe",
            "1": "Critical"
        },

        file,

        indent=4

    )


# ==========================================
# 30. SAVE TRAINING INFORMATION
# ==========================================

training_info = {

    "model": "distilbert-base-uncased",

    "classes": 2,

    "labels": {

        "0": "Safe",

        "1": "Critical"

    },

    "dataset_size": len(df),

    "training_samples": len(X_train),

    "testing_samples": len(X_test),

    "max_length": MAX_LENGTH,

    "epochs": 3,

    "accuracy": float(accuracy)

}


info_file = os.path.join(

    MODEL_DIR,

    "training_info.json"

)


with open(

    info_file,

    "w",

    encoding="utf-8"

) as file:

    json.dump(

        training_info,

        file,

        indent=4

    )


# ==========================================
# 31. FINAL MESSAGE
# ==========================================

print("\n")
print("=" * 60)
print("TEXT MODEL TRAINING COMPLETED!")
print("=" * 60)


print("\nModel Saved At:")

print(
    MODEL_DIR
)


print("\nLabel Mapping:")

print("0 -> Safe")
print("1 -> Critical")


print("\nFinal Accuracy:")

print(
    f"{accuracy * 100:.2f}%"
)


print("\nSentriX Text Model is Ready!")