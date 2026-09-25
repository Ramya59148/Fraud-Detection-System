import pandas as pd

# Dataset path
file_path = r"C:\Users\Ramya R\Desktop\Sentrix\dataSets\email_dataset.csv"


# Load dataset
data = pd.read_csv(
    file_path,
    encoding="latin1"
)


# Remove unnecessary column
data = data.drop(
    columns=["Unnamed: 0"]
)


# Rename columns
data.rename(
    columns={
        "Email Text": "text",
        "Email Type": "label"
    },
    inplace=True
)


# Remove missing values
data.dropna(inplace=True)


# Remove duplicate emails
data.drop_duplicates(inplace=True)


print("After Cleaning:")
print(data.head())


print("\nDataset Shape:")
print(data.shape)


print("\nLabels:")
print(data["label"].value_counts())


# Convert labels for SentriX

data["label"] = data["label"].replace(
    {
        "Safe Email": "Safe",
        "Phishing Email": "Critical"
    }
)


print("\nSentriX Labels:")
print(data["label"].value_counts())


# Save cleaned dataset

output_path = r"C:\Users\Ramya R\Desktop\Sentrix\dataSets\clean_email_dataset.csv"

data.to_csv(
    output_path,
    index=False
)


print("\nClean email dataset saved!")