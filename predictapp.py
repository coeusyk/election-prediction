import pandas as pd
import plotly.express as px
from shiny import App, render, ui, reactive
import shinywidgets  # Required for Plotly support

# Load prediction data
df_2029 = pd.read_csv("predicted_2029_results.csv")

# Ensure data types are correct
df_2029["STATE NAME"] = df_2029["STATE NAME"].astype(str)
df_2029["PARTY NAME"] = df_2029["PARTY NAME"].astype(str)
df_2029["SEATS WON"] = df_2029["SEATS WON"].astype(int)

# Get unique state names
state_options = sorted(df_2029["STATE NAME"].dropna().unique())

# Define UI
app_ui = ui.page_fluid(
    ui.h2("Election Prediction for 2029", class_="text-center"),

    ui.layout_sidebar(
        ui.sidebar(
            ui.input_select("state", "Select State:", state_options, selected=state_options[0])
        ),

        ui.div(
            ui.card(
                ui.h4("Predicted Seats Won"),
                shinywidgets.output_widget("prediction_chart")
            ),
            ui.card(
                ui.h4("Seats Won Summary Table"),
                ui.output_table("prediction_table")
            )
        )
    )
)


# Define Server Logic
def server(input, output, session):
    @reactive.calc
    def filtered_data():
        """Filter predictions based on selected state"""
        return df_2029[df_2029["STATE NAME"] == input.state()]

    @output
    @shinywidgets.render_widget
    def prediction_chart():
        """Bar chart of predicted seats won"""
        data = filtered_data()
        fig = px.bar(
            data,
            x="PARTY NAME",
            y="SEATS WON",
            color="PARTY NAME",
            title=f"Predicted Seats Won in {input.state()} (2029)",
            labels={"SEATS WON": "Seats Won"}
        )
        return fig

    @output
    @render.table
    def prediction_table():
        """Table summary of predicted seats"""
        return filtered_data()[["PARTY NAME", "SEATS WON"]]


# Run the app
app = App(app_ui, server)
