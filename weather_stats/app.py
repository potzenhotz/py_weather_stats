import pandas as pd
import os
import dash
import dash_html_components as html
import dash_core_components as dcc
import plotly.express as px

dir_path = os.path.dirname(os.path.realpath(__file__))
df_weather_daily = pd.read_csv(
    f"{dir_path}/data/produkt_klima_tag_19350101_20191231_01303.txt", sep=";"
)
# Remove whitespaces from header
df_weather_daily = df_weather_daily.rename(columns=lambda x: x.strip())

df_weather_daily["MESS_DATUM"] = pd.to_datetime(
    df_weather_daily["MESS_DATUM"], format="%Y%m%d"
)
df_weather_daily["year"] = pd.DatetimeIndex(df_weather_daily["MESS_DATUM"]).year
df_weather_daily["month"] = pd.DatetimeIndex(df_weather_daily["MESS_DATUM"]).month
df_weather_daily["day"] = pd.DatetimeIndex(df_weather_daily["MESS_DATUM"]).day
df_weather_daily["period"] = (
    df_weather_daily["month"].astype(str) + "-" + df_weather_daily["day"].astype(str)
)
# df_temp_daily = df_weather_daily.pivot(index="period", columns="year", values="TMK")

df_test = df_weather_daily[(df_weather_daily["year"].astype(str).str.contains("197"))]

print(df_test.head(50))

app = dash.Dash(__name__)
app.layout = html.Div(
    children=[
        html.H2("Dashboard - Weather Stats"),
        html.P("Visualising weather data with Plotly - Dash"),
        html.Div(
            className="row",
            children=[
                html.Div(className="four columns div-user-controls"),
                html.Div(
                    className="eight columns div-for-charts bg-grey",
                    children=[
                        dcc.Graph(
                            id="timeseries",
                            config={"displayModeBar": False},
                            animate=True,
                            figure=px.line(
                                df_test,
                                x="period",
                                y="TMK",
                                color="year",
                                template="plotly_dark",
                            ).update_layout(
                                {
                                    "plot_bgcolor": "rgba(0, 0, 0, 0)",
                                    "paper_bgcolor": "rgba(0, 0, 0, 0)",
                                }
                            ),
                        )
                    ],
                ),
            ],
        ),
    ]
)

if __name__ == "__main__":
    app.run_server(debug=True)
