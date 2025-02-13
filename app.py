import pandas as pd
import plotly.express as px
from shiny import App, render, ui, reactive
import shinywidgets  # Required for Plotly support

# Load datasets for historical results
df_2014 = pd.read_csv("filtered_datasets/top_3_parties_per_state_2014.csv")
df_2019 = pd.read_csv("filtered_datasets/top_3_parties_per_state_2019.csv")
df_2024 = pd.read_csv("filtered_datasets/top_3_parties_per_state_2024.csv")

df_2014["Year"] = 2014
df_2019["Year"] = 2019
df_2024["Year"] = 2024

df = pd.concat([df_2014, df_2019, df_2024], ignore_index=True)

df["STATE NAME"] = df["STATE NAME"].astype(str)
df["PARTY NAME"] = df["PARTY NAME"].astype(str)
df["Year"] = df["Year"].astype(int)

state_options = sorted(df["STATE NAME"].dropna().unique())
year_options = [str(y) for y in sorted(df["Year"].unique())]

# Load prediction data
df_2029 = pd.read_csv("predicted_2029_results.csv")

df_2029["State"] = df_2029["State"].astype(str)
df_2029["Party"] = df_2029["Party"].astype(str)
df_2029["Seats_Won"] = df_2029["Seats_Won"].astype(int)

prediction_state_options = sorted(df_2029["State"].dropna().unique())

# Define UI
app_ui = ui.page_fluid(
    ui.navset_tab(
    ui.nav_panel("Historical Data",
        ui.layout_sidebar(
                     ui.sidebar(
                         ui.input_select("year", "Select Year", year_options, selected="2024"),
                         ui.input_select("state", "Select State", state_options, selected=state_options[0])
                     ),
                     ui.div(
                         ui.card(
                             ui.h4("Seats Won by Top 3 Parties"),
                             ui.output_ui("seats_won_chart")
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
        ),
        ui.nav_panel("Predictions",
        ui.layout_sidebar(
                 ui.sidebar(
                     ui.input_select("pred_state", "Select State:", prediction_state_options,
                                     selected=prediction_state_options[0])
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
    )
)


# Define Server Logic
def server(input, output, session):
    # Historical Data Logic
    @reactive.calc
    def filtered_data():
        return df[(df["Year"] == int(input.year())) & (df["STATE NAME"] == input.state())]

    @output
    @render.ui
    def seats_won_chart():
        data = filtered_data()
        if data.empty:
            return ui.HTML("<p style='color: red; font-weight: bold;'>No data available for this selection.</p>")

        fig = px.bar(data, x="PARTY NAME", y="SEATS WON", color="PARTY NAME",
                     title=f"Seats Won by Top 3 Parties in {input.state()} ({input.year()})",
                     labels={"SEATS WON": "Number of Seats"})

        return ui.HTML(fig.to_html(full_html=False, include_plotlyjs='cdn'))

    @output
    @shinywidgets.render_widget
    def party_trend_chart():
        party_data = df[df["STATE NAME"] == input.state()]
        fig = px.line(party_data, x="Year", y="SEATS WON", color="PARTY NAME", markers=True,
                      title=f"Party Performance Over Years in {input.state()}",
                      labels={"SEATS WON": "Seats Won"})
        return fig

    @output
    @render.table
    def seats_won_table():
        return filtered_data()[["PARTY NAME", "SEATS WON", "% SEATS WON"]]

    # Prediction Logic
    @reactive.calc
    def filtered_prediction():
        return df_2029[df_2029["State"] == input.pred_state()]

    @output
    @shinywidgets.render_widget
    def prediction_chart():
        data = filtered_prediction()
        fig = px.bar(data, x="Party", y="Seats_Won", color="Party",
                     title=f"Predicted Seats Won in {input.pred_state()} (2029)",
                     labels={"Seats_Won": "Seats Won"})
        return fig

    @output
    @render.table
    def prediction_table():
        return filtered_prediction()[["Party", "Seats_Won"]]


# Run the app
app = App(app_ui, server)
