import pandas as pd
import plotly.express as px
from shiny import App, render, ui, reactive
import shinywidgets  # Required for Plotly support

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

# Get unique state names and years (convert years to strings for UI compatibility)
state_options = sorted(df["STATE NAME"].dropna().unique())
year_options = [str(y) for y in sorted(df["Year"].unique())]

# Define UI
app_ui = ui.page_fluid(
    ui.h2("Multi-Year Election Analysis", class_="text-center"),

    ui.layout_sidebar(
        ui.sidebar(
            ui.input_select("year", "Select Year", year_options, selected="2024"),
            ui.input_select("state", "Select State", state_options, selected=state_options[0])
        ),

        ui.div(
            ui.card(
                ui.h4("Seats Won by Top 3 Parties"),
                ui.output_ui("seats_won_chart")  # FIX: Use output_ui to handle both Plotly & HTML
            ),
            ui.card(
                ui.h4("Party Performance Over Years"),
                shinywidgets.output_widget("party_trend_chart")
            ),
            ui.card(
                ui.h4("Seats Won Summary Table"),
                ui.output_table("seats_won_table")
            )
        )
    )
)


# Define Server Logic
def server(input, output, session):
    @reactive.calc
    def filtered_data():
        """Filter data based on selected year & state"""
        return df[(df["Year"] == int(input.year())) & (df["STATE NAME"] == input.state())]

    @output
    @render.ui  # FIX: Use render.ui to handle both Plotly and "No data" message
    def seats_won_chart():
        """Bar chart of seats won by the top 3 parties"""
        data = filtered_data()
        if data.empty:
            return ui.HTML("<p style='color: red; font-weight: bold;'>No data available for this selection.</p>")

        fig = px.bar(
            data,
            x="PARTY NAME",
            y="SEATS WON",
            color="PARTY NAME",
            title=f"Seats Won by Top 3 Parties in {input.state()} ({input.year()})",
            labels={"SEATS WON": "Number of Seats"}
        )
        return ui.HTML(fig.to_html(full_html=False, include_plotlyjs='cdn'))  # Convert Plotly to HTML

    @output
    @shinywidgets.render_widget
    def party_trend_chart():
        """Line chart showing party performance over years"""
        party_data = df[df["STATE NAME"] == input.state()]
        fig = px.line(
            party_data,
            x="Year",
            y="SEATS WON",
            color="PARTY NAME",
            markers=True,
            title=f"Party Performance Over Years in {input.state()}",
            labels={"SEATS WON": "Seats Won"}
        )
        return fig

    @output
    @render.table
    def seats_won_table():
        """Table summary of seats won"""
        return filtered_data()[["PARTY NAME", "SEATS WON", "% SEATS WON"]]


# Run the app
app = App(app_ui, server)
