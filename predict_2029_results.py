import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
import xgboost as xgb


# File paths
file_2014 = "filtered_datasets/top_3_parties_per_state_2014.csv"
file_2019 = "filtered_datasets/top_3_parties_per_state_2019.csv"
file_2024 = "filtered_datasets/top_3_parties_per_state_2024.csv"

# Load datasets
df_2014 = pd.read_csv(file_2014)
df_2019 = pd.read_csv(file_2019)
df_2024 = pd.read_csv(file_2024)


# Standardize column names & preprocess data
def preprocess_data(df, year):
    df = df.copy()
    df["Year"] = year
    df = df.rename(columns={
        "STATE NAME": "State",
        "PARTY NAME": "Party",
        "SEATS WON": "Seats_Won",
        "TOTAL SEATS IN STATE": "Total_Seats",
        "TOTAL VALID VOTES POLLED BY PARTY": "Votes_Party",
        "% OF VALID VOTES POLLED BY PARTY": "Votes_Percentage",
    })
    df = df[["State", "Party", "Year", "Votes_Party", "Votes_Percentage", "Seats_Won", "Total_Seats"]]
    df.fillna(0, inplace=True)  # Handle missing values
    return df

# Preprocess all datasets
df_2014 = preprocess_data(df_2014, 2014)
df_2019 = preprocess_data(df_2019, 2019)
df_2024 = preprocess_data(df_2024, 2024)

# Combine data
df = pd.concat([df_2014, df_2019, df_2024], ignore_index=True)

# Encode categorical features (State, Party)
label_encoders = {}
for col in ["State", "Party"]:
    le = LabelEncoder()
    df[col] = le.fit_transform(df[col])
    label_encoders[col] = le

# Define features & target
X = df[["State", "Party", "Year", "Votes_Party", "Votes_Percentage", "Total_Seats"]]
y = df["Seats_Won"]

# Train-test split
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Train XGBoost model (optimized settings)
model = xgb.XGBRegressor(objective="reg:squarederror", n_estimators=50, learning_rate=0.1, max_depth=3)
model.fit(X_train, y_train)

# Prepare 2029 prediction data
df_2029 = df_2024.copy()
df_2029["Year"] = 2029

# Reapply label encoding for 2029 data
df_2029["State"] = label_encoders["State"].transform(df_2029["State"])
df_2029["Party"] = label_encoders["Party"].transform(df_2029["Party"])

# Predict seats for 2029
df_2029["Seats_Won"] = model.predict(df_2029[["State", "Party", "Year", "Votes_Party", "Votes_Percentage", "Total_Seats"]])
df_2029["Seats_Won"] = np.round(df_2029["Seats_Won"]).astype(int)  # Ensure integer values

# Convert back to original labels for readability
df_2029["State"] = label_encoders["State"].inverse_transform(df_2029["State"])
df_2029["Party"] = label_encoders["Party"].inverse_transform(df_2029["Party"])

# Save final predictions
df_2029.to_csv("predicted_2029_results.csv", index=False)
print("✅ Predictions saved to 'predicted_2029_results.csv'.")

# Show preview
print(df_2029.head())
