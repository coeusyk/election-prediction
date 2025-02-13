import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
import plotly.express as px

# Load datasets for different years
df_2014 = pd.read_csv("output/top_3_parties_per_state_2014.csv")
df_2019 = pd.read_csv("output/top_3_parties_per_state_2019.csv")
df_2024 = pd.read_csv("output/top_3_parties_per_state_2024.csv")

# Add a "Year" column to each dataset
df_2014["Year"] = 2014
df_2019["Year"] = 2019
df_2024["Year"] = 2024

# Combine all datasets into one
df = pd.concat([df_2014, df_2019, df_2024], ignore_index=True)

# Ensure data types are correct
df["STATE NAME"] = df["STATE NAME"].astype(str)
df["PARTY NAME"] = df["PARTY NAME"].astype(str)
df["Year"] = df["Year"].astype(int)

# Create an empty DataFrame to store predictions
predictions = []

# Train a model for each state & party
for (state, party), group in df.groupby(["STATE NAME", "PARTY NAME"]):
    if len(group) < 2:  # Need at least two data points for prediction
        continue

    X = group[["Year"]]
    y = group["SEATS WON"]

    model = LinearRegression()
    model.fit(X, y)  # Train model

    # Predict 2029 seats
    predicted_seats = model.predict([[2029]])[0]
    predicted_seats = max(0, round(predicted_seats))  # Ensure no negative seats

    # Store prediction
    predictions.append({"STATE NAME": state, "PARTY NAME": party, "Year": 2029, "SEATS WON": predicted_seats})

# Convert predictions to DataFrame
df_2029 = pd.DataFrame(predictions)

# Save predictions to CSV
df_2029.to_csv("predicted_2029_results.csv", index=False)
print("✅ Predictions saved to 'predicted_2029_results.csv'.")

# Visualization
fig = px.bar(
    df_2029,
    x="STATE NAME",
    y="SEATS WON",
    color="PARTY NAME",
    title="Predicted Seats for 2029 Election",
    labels={"SEATS WON": "Seats Won"},
    barmode="stack"
)
fig.show()
