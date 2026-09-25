import torch
from transformers import DistilBertTokenizer, DistilBertForSequenceClassification

MODEL_PATH = "training/saved_models/text_model"

tokenizer = DistilBertTokenizer.from_pretrained(
    MODEL_PATH,
    local_files_only=True
)

model = DistilBertForSequenceClassification.from_pretrained(
    MODEL_PATH,
    local_files_only=True
)

model.eval()

print("======================================")
print("       SENTRIX TEXT DETECTION")
print("======================================")

while True:

    text = input("\nEnter text (or type exit): ")

    if text.lower() == "exit":
        print("Program stopped.")
        break

    inputs = tokenizer(
        text,
        return_tensors="pt",
        truncation=True,
        padding=True,
        max_length=128
    )

    with torch.no_grad():
        outputs = model(**inputs)

    probabilities = torch.softmax(outputs.logits, dim=1)
    prediction = torch.argmax(probabilities, dim=1).item()
    confidence = probabilities[0][prediction].item() * 100

    if prediction == 0:
        result = "Safe"
    else:
        result = "Critical"

    print("\n--------------------------------------")
    print("Input      :", text)
    print("Prediction :", result)
    print("Confidence :", f"{confidence:.2f}%")
    print("--------------------------------------")