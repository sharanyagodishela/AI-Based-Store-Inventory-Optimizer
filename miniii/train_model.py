import pandas as pd
import os
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
import pickle

# -----------------------------
# LOAD DATASET
# -----------------------------
file_path = "stores.csv"

print("Loading dataset...")

if not os.path.exists(file_path):
    print(f"Error: {file_path} not found! Please place stores.csv in the project folder.")
    exit()

try:
    data = pd.read_csv(file_path)
except Exception as e:
    print(f"Error reading CSV file: {e}")
    exit()

# Clean column names
data.columns = data.columns.str.strip()

print("Dataset loaded successfully!\n")

# Preview dataset
print("First 5 rows of dataset:")
print(data.head())

# -----------------------------
# HANDLE MISSING VALUES
# -----------------------------
if data.isnull().sum().sum() > 0:
    print("\nMissing values found. Filling with mean values...")
    data = data.fillna(data.mean(numeric_only=True))
else:
    print("\nNo missing values found.")

# -----------------------------
# SELECT FEATURES AND TARGET
# -----------------------------
try:
    X = data[['Store_Area', 'Items_Available', 'Daily_Customer_Count']]
    y = data['Store_Sales']
except KeyError as e:
    print(f"Column missing in CSV file: {e}")
    exit()

# -----------------------------
# TRAIN TEST SPLIT
# -----------------------------
X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.2,
    random_state=42
)

# -----------------------------
# TRAIN MODEL
# -----------------------------
print("\nTraining model...")

model = LinearRegression()
model.fit(X_train, y_train)

# -----------------------------
# MODEL EVALUATION
# -----------------------------
train_score = model.score(X_train, y_train)
test_score = model.score(X_test, y_test)

print("\n------ MODEL PERFORMANCE ------")
print(f"Training Score (R²): {train_score:.2f}")
print(f"Testing Score (R²): {test_score:.2f}")

# -----------------------------
# PRINT MODEL DETAILS (FOR VIVA)
# -----------------------------
print("\nModel Coefficients:")
for feature, coef in zip(X.columns, model.coef_):
    print(f"{feature}: {coef:.2f}")

print(f"Intercept: {model.intercept_:.2f}")

# -----------------------------
# SAVE MODEL + FEATURES
# -----------------------------
model_file = "model.pkl"

model_data = {
    "model": model,
    "features": list(X.columns)
}

with open(model_file, "wb") as f:
    pickle.dump(model_data, f)

# -----------------------------
# FINAL OUTPUT
# -----------------------------
print("\n------ TRAINING COMPLETE ------")
print("Model trained and saved successfully!")
print(f"Saved file: {model_file}")