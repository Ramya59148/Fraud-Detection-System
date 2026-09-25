import pandas as pd

# Dataset path
file_path = r"C:\Users\Ramya R\Desktop\Sentrix\dataSets\text_dataset.csv"

# Step 1: Load dataset
data = pd.read_csv(
    file_path,
    sep="\t",
    encoding="latin1"
)

print("Original Dataset:")
print(data.head())

print("\nOriginal Shape:")
print(data.shape)


# Step 2: Keep only required columns
data = data[['v1', 'v2']]


# Step 3: Rename columns
data.rename(
    columns={
        "v1": "label",
        "v2": "text"
    },
    inplace=True
)


# Step 4: Remove missing values
data.dropna(inplace=True)


# Step 5: Remove duplicate messages
data.drop_duplicates(inplace=True)


print("\nAfter Cleaning:")
print(data.head())


print("\nClean Dataset Shape:")
print(data.shape)


# Step 6: Check original labels
print("\nOriginal Labels:")
print(data["label"].value_counts())


# Step 7: Convert labels for SentriX project
# ham  -> Safe
# spam -> Critical

data["label"] = data["label"].replace(
    {
        "ham": "Safe",
        "spam": "Critical"
    }
)


print("\nNew Labels:")
print(data["label"].value_counts())


# Step 8: Save cleaned dataset

output_path = r"C:\Users\Ramya R\Desktop\Sentrix\dataSets\clean_text_dataset.csv"

data.to_csv(
    output_path,
    index=False
)


print("\nClean dataset saved successfully!")
print(output_path)