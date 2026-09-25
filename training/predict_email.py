# ==========================================
# SENTRIX - EMAIL PREDICTION
# ==========================================

import os
import torch
from transformers import (
    DistilBertTokenizer,
    DistilBertForSequenceClassification
)

# ==========================================
# 1. MODEL PATH
# ==========================================

model_path = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    "saved_models",
    "email_model"
)

print("=" * 60)
print("SENTRIX - EMAIL AI DETECTOR")
print("=" * 60)

print("\nModel Path:")
print(model_path)

# ==========================================
# 2. CHECK MODEL
# ==========================================

if not os.path.exists(model_path):
    raise FileNotFoundError(
        f"\nModel not found:\n{model_path}"
    )

print("\nLocal model found successfully!")

# ==========================================
# 3. DEVICE
# ==========================================

device = torch.device(
    "cuda" if torch.cuda.is_available() else "cpu"
)

print("Using Device:", device)

# ==========================================
# 4. LOAD TOKENIZER
# ==========================================

print("\nLoading tokenizer...")

tokenizer = DistilBertTokenizer.from_pretrained(
    model_path,
    local_files_only=True
)

print("Tokenizer loaded successfully!")

# ==========================================
# 5. LOAD TRAINED MODEL
# ==========================================

print("\nLoading trained Email model...")

model = DistilBertForSequenceClassification.from_pretrained(
    model_path,
    local_files_only=True
)

model.to(device)

model.eval()

print("Email model loaded successfully!")

# ==========================================
# 6. LABEL MAPPING
# ==========================================

# Based on your email dataset
# LabelEncoder created:
#
# Critical -> 0
# Safe     -> 1
#
# We will verify this using the model configuration.

label_mapping = {
    0: "Critical",
    1: "Safe"
}

print("\nLabel Mapping:")
print(label_mapping)

# ==========================================
# 7. PREDICTION FUNCTION
# ==========================================

def predict_email(email_text):

    # Tokenize email
    inputs = tokenizer(
        email_text,
        return_tensors="pt",
        truncation=True,
        padding=True,
        max_length=128
    )

    # Move tensors to CPU/GPU
    inputs = {
        key: value.to(device)
        for key, value in inputs.items()
    }

    # Disable gradient calculation
    with torch.no_grad():

        outputs = model(
            **inputs
        )

    # Convert logits to probabilities
    probabilities = torch.softmax(
        outputs.logits,
        dim=1
    )

    # Get predicted class
    predicted_id = torch.argmax(
        probabilities,
        dim=1
    ).item()

    # Get confidence
    confidence = (
        probabilities[0][predicted_id].item()
        * 100
    )

    predicted_label = label_mapping[
        predicted_id
    ]

    return predicted_label, confidence, probabilities


# ==========================================
# 8. USER INPUT
# ==========================================

print("\n")
print("=" * 60)
print("EMAIL ANALYSIS")
print("=" * 60)

print("\nType an email/message.")
print("Type 'exit' to close the program.\n")

while True:

    email_text = input("Enter Email: ")

    if email_text.lower() == "exit":
        print("\nSentrix Email Detector Closed.")
        break

    if not email_text.strip():

        print("\nPlease enter some text.\n")
        continue

    # Predict
    label, confidence, probabilities = predict_email(
        email_text
    )

    # ==========================================
    # DISPLAY RESULT
    # ==========================================

    print("\n")
    print("-" * 60)
    print("SENTRIX ANALYSIS RESULT")
    print("-" * 60)

    print("Prediction :", label)
    print(f"Confidence : {confidence:.2f}%")

    print("-" * 60)

    # Display both class probabilities

    print(
        f"Critical Probability : "
        f"{probabilities[0][0].item() * 100:.2f}%"
    )

    print(
        f"Safe Probability     : "
        f"{probabilities[0][1].item() * 100:.2f}%"
    )

    print("-" * 60)