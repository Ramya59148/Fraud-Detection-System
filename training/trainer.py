import os
import torch

from torch.utils.data import DataLoader
from torch.optim import AdamW

from transformers import DistilBertForSequenceClassification

from sklearn.metrics import accuracy_score


# ==========================================
# Device
# ==========================================

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

print("Using Device:", device)


# ==========================================
# Create DataLoaders
# ==========================================

def create_dataloaders(train_dataset, test_dataset, batch_size=16):

    train_loader = DataLoader(
        train_dataset,
        batch_size=batch_size,
        shuffle=True
    )

    test_loader = DataLoader(
        test_dataset,
        batch_size=batch_size,
        shuffle=False
    )

    return train_loader, test_loader


# ==========================================
# Load DistilBERT Model
# ==========================================

def load_model(num_labels):

    model = DistilBertForSequenceClassification.from_pretrained(
        "distilbert-base-uncased",
        num_labels=num_labels
    )

    model.to(device)

    return model


# ==========================================
# Create Optimizer
# ==========================================

def create_optimizer(model):

    optimizer = AdamW(
        model.parameters(),
        lr=2e-5
    )

    return optimizer


# ==========================================
# Train Model
# ==========================================

def train_model(
    model,
    train_loader,
    optimizer,
    device,
    epochs=3
):

    model.train()

    for epoch in range(epochs):

        print(f"\n========== Epoch {epoch+1}/{epochs} ==========")

        total_loss = 0

        for batch in train_loader:

            input_ids = batch["input_ids"].to(device)
            attention_mask = batch["attention_mask"].to(device)
            labels = batch["labels"].to(device)

            optimizer.zero_grad()

            outputs = model(
                input_ids=input_ids,
                attention_mask=attention_mask,
                labels=labels
            )

            loss = outputs.loss

            total_loss += loss.item()

            loss.backward()

            optimizer.step()

        avg_loss = total_loss / len(train_loader)

        print(f"Average Loss : {avg_loss:.4f}")

    print("\nTraining Completed Successfully!")


# ==========================================
# Evaluate Model
# ==========================================

def evaluate_model(model, test_loader, device):

    model.eval()

    predictions = []
    actual = []

    with torch.no_grad():

        for batch in test_loader:

            input_ids = batch["input_ids"].to(device)
            attention_mask = batch["attention_mask"].to(device)
            labels = batch["labels"].to(device)

            outputs = model(
                input_ids=input_ids,
                attention_mask=attention_mask
            )

            preds = torch.argmax(outputs.logits, dim=1)

            predictions.extend(preds.cpu().numpy())
            actual.extend(labels.cpu().numpy())

    accuracy = accuracy_score(actual, predictions)

    print(f"\nModel Accuracy : {accuracy * 100:.2f}%")

    return accuracy


# ==========================================
# Save Model
# ==========================================

#def save_model(model, save_path):

    os.makedirs(save_path, exist_ok=True)

    model.save_pretrained(save_path)

    print("\nModel Saved Successfully!")
 #   print("Saved At :", save_path)

# ==========================================
# SAVE MODEL
# ==========================================

def save_model(model, path):

    os.makedirs(path, exist_ok=True)

    model.save_pretrained(path)

    print("\nModel Saved Successfully!")
    print("Saved At:", os.path.abspath(path))