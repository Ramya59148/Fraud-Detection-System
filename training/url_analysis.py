import pandas as pd


# URL dataset path
file_path = r""


# Load dataset
data = pd.read_csv(
    file_path,
    encoding="latin1"
)


print("Original Dataset:")
print(data.head())


# Keep only required columns
data = data[['url', 'type']]


# Rename columns
data.rename(
    columns={
        "type": "label"
    },
    inplace=True
)


# Remove missing values
data.dropna(inplace=True)


# Remove duplicate URLs
data.drop_duplicates(inplace=True)


print("\nAfter Cleaning:")
print(data.head())


print("\nDataset Shape:")
print(data.shape)


print("\nOriginal Labels:")
print(data['label'].value_counts())


# Convert labels to SentriX categories

data["label"] = data["label"].replace(
    {
        "benign": "Safe",
        "phishing": "Critical",
        "malware": "Critical",
        "defacement": "Suspicious"
    }
)


print("\nSentriX Labels:")
print(data["label"].value_counts())


# Save cleaned dataset

output_path = r"C:\Users\Ramya R\Desktop\Sentrix\dataSets\clean_url_dataset.csv"


data.to_csv(
    output_path,
    index=False
)


print("\nClean URL dataset saved successfully!")
print(output_path)