import pandas as pd

def process_election_data(file_path, output_file):
    """
    Processes election data to find the top 3 parties in each state based on seats won
    and calculates the percentage of seats won.
    """
    # Load the CSV file, skipping the first row to fix column headers
    df = pd.read_csv(file_path, skiprows=1)

    # Rename columns properly
    df.columns = [
        "STATE NAME", "PARTY TYPE", "PARTY NAME", "TOTAL VALID VOTES POLLED IN STATE",
        "TOTAL ELECTORS IN STATE", "SEATS WON", "TOTAL VALID VOTES POLLED BY PARTY", "% OF VALID VOTES POLLED BY PARTY"
    ]

    # Convert 'SEATS WON' to numeric (ignoring errors for non-numeric values)
    df["SEATS WON"] = pd.to_numeric(df["SEATS WON"], errors="coerce")

    # Group by State and get the top 3 parties based on seats won
    top_parties = df.groupby("STATE NAME").apply(lambda x: x.nlargest(3, "SEATS WON")).reset_index(drop=True)

    # Calculate total seats in each state
    total_seats_per_state = df.groupby("STATE NAME")["SEATS WON"].sum().reset_index()
    total_seats_per_state.columns = ["STATE NAME", "TOTAL SEATS IN STATE"]

    # Merge with top parties data
    top_parties = top_parties.merge(total_seats_per_state, on="STATE NAME", how="left")

    # Compute % of seats won
    top_parties["% SEATS WON"] = (top_parties["SEATS WON"] / top_parties["TOTAL SEATS IN STATE"]) * 100

    # Save the results to a CSV file
    top_parties.to_csv(output_file, index=False)

    print(f"Analysis complete! Results saved to {output_file}")

# Process  election data
process_election_data("datasets/State-Wise-Seat-Won_2014.csv", "filtered_datasets/top_3_parties_per_state_2014.csv")
process_election_data("datasets/State-Wise-Seat-Won_2019.csv", "filtered_datasets/top_3_parties_per_state_2019.csv")
process_election_data("datasets/State-Wise-Seat-Won_2024.csv", "filtered_datasets/top_3_parties_per_state_2024.csv")
