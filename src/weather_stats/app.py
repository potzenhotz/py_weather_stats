import os
import dash
from dash import html
from dash import dcc
from dash.dependencies import Input, Output
import plotly.express as px
import plotly.graph_objects as go
from weather_data import weather_station


ws = weather_station()
# df_weather = ws.get_weather_df(testing=True)
df_weather = ws.df_weather_data
df_stations = ws.df_stations_info
current_station = ws.station_name
# df_temp = ws.get_temp_df()

external_stylesheets = ["https://codepen.io/chriddyp/pen/bWLwgP.css"]

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

# fig = px.line(df_temp, x="period", y=2000,)
# fig.add_scatter(df_temp, x="period", y=2001, mode="lines")

# fig_temp = px.line(df_weather, x="period", y="TMK", color="year", title="Temperature")
# fig_temp.update_layout(xaxis=dict(tickformat="%d-%b"))

# fig_press = px.line(df_weather, x="period", y="PM", color="year", title="Pressure")
# fig_press.update_layout(xaxis=dict(tickformat="%d-%b"))


app.layout = html.Div(
    children=[
        html.H1(children="Hello Dash"),
        html.Div(
            children="""
        Dash: A web application framework for Python.
    """
        ),
        html.Br(),
        html.Div(
            [
                html.Label("Station:", id="station-label"),
                dcc.Dropdown(
                    id="station-dropdown",
                    options=[
                        {"label": i, "value": i}
                        for i in df_stations.Stationsname.unique()
                    ],
                    placeholder="Select weather station...",
                    value="Essen-Bredeney",
                ),
            ]
        ),
        html.Br(),
        html.Div(
            [
                html.Label("Year Slider", id="time-range-label"),
                dcc.RangeSlider(
                    id="year-slider",
                    min=df_weather["year"].min(),
                    max=df_weather["year"].max(),
                    value=[df_weather["year"].min(), df_weather["year"].max()],
                    marks={
                        str(year): str(year)
                        for year in df_weather["year"].unique()
                        if year % 5 == 0
                    },
                    step=1,
                ),
            ]
        ),
        html.Br(),
        html.Div(
            [
                html.Label("Period Slider", id="period-range-label"),
                dcc.RangeSlider(
                    id="period-slider",
                    min=df_weather["period_int"].min(),
                    max=df_weather["period_int"].max(),
                    value=[
                        df_weather["period_int"].min(),
                        df_weather["period_int"].max(),
                    ],
                    marks={
                        str(period): str(period)
                        for period in df_weather["period_int"].unique()
                        # if period % 2 == 0
                    },
                    step=1,
                ),
            ]
        ),
        dcc.Graph(id="temp_graph"),
        dcc.Graph(id="press_graph"),
        dcc.Graph(id="precip_graph"),
        dcc.Graph(id="cover_graph"),
        dcc.Graph(id="wind_mean_graph"),
    ]
)


@app.callback(
    [
        Output("temp_graph", "figure"),
        Output("press_graph", "figure"),
        Output("precip_graph", "figure"),
        Output("cover_graph", "figure"),
        Output("wind_mean_graph", "figure"),
        Output("year-slider", "min"),
        Output("year-slider", "max"),
    ],
    [
        Input("year-slider", "value"),
        Input("period-slider", "value"),
        Input("station-dropdown", "value"),
    ],
)
def update_figure(selected_years, selected_period, selected_station):
    global df_weather
    global current_station
    if current_station != selected_station:
        print(selected_station)
        ws.change_station_df(selected_station)
        df_weather = ws.df_weather_data
        df_filtered = df_weather[
            (df_weather.year >= df_weather["year"].min())
            & (df_weather.year <= df_weather["year"].max())
        ]
    else:
        print(f"updating years {selected_years}")
        df_filtered = df_weather[
            (df_weather.year >= selected_years[0])
            & (df_weather.year <= selected_years[1])
        ]
    current_station = selected_station
    df_filtered = df_filtered[
        (df_filtered.period_int >= selected_period[0])
        & (df_filtered.period_int <= selected_period[1])
    ]
    df_grp_period = df_filtered.groupby(["period"]).mean()
    print(df_grp_period)

    fig_temp = px.line(
        df_filtered, x="period", y="TMK", color="year", title="Temperature"
    )
    fig_temp.update_layout(xaxis=dict(tickformat="%d-%b"))

    fig_press = px.line(df_filtered, x="period", y="PM", color="year", title="Pressure")
    fig_press.update_layout(xaxis=dict(tickformat="%d-%b"))
    fig_precip = px.bar(
        df_filtered,
        x="period",
        y="RSK",
        color="year",
        title="Precipitation",
        barmode="overlay",
    )
    fig_precip.update_layout(xaxis=dict(tickformat="%d-%b"))

    fig_cover = px.line(
        df_grp_period,
        x=df_grp_period.index,
        y="NM",
        # color="year",
        title="Cloud Coverage",
    )
    fig_cover.update_layout(xaxis=dict(tickformat="%d-%b"))

    fig_wind_mean = px.line(
        df_filtered,
        x="period",
        y="FM",
        color="year",
        title="Wind Daily Mean",
    )
    fig_wind_mean.update_layout(xaxis=dict(tickformat="%d-%b"))

    year_min = df_weather["year"].min()
    year_max = df_weather["year"].max()

    return fig_temp, fig_press, fig_precip, fig_cover, fig_wind_mean, year_min, year_max


if __name__ == "__main__":
    app.run_server(debug=True)
