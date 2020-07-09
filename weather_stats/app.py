import os
import dash
import dash_html_components as html
import dash_core_components as dcc
from dash.dependencies import Input, Output
import plotly.express as px
import plotly.graph_objects as go
import weather_data as wd


ws = wd.weather_station()
df_weather = ws.get_weather_df(testing=True)
df_weather = ws.get_weather_df()
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
        html.Br(),
        html.Div(
            [
                html.Label("Year Slider", id="time-range-label"),
                dcc.RangeSlider(
                    id="year-slider",
                    min=df_weather["year"].min(),
                    max=df_weather["year"].max(),
                    value=[2000, df_weather["year"].max()],
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
    ]
)


@app.callback(
    [
        Output("temp_graph", "figure"),
        Output("press_graph", "figure"),
        Output("precip_graph", "figure"),
        Output("cover_graph", "figure"),
    ],
    [Input("year-slider", "value"), Input("period-slider", "value")],
)
def update_figure(selected_years, selected_period):
    # df_filtered = df_weather[df_weather.year == selected_year]
    df_filtered = df_weather[
        (df_weather.year >= selected_years[0]) & (df_weather.year <= selected_years[1])
    ]
    df_filtered = df_filtered[
        (df_filtered.period_int >= selected_period[0])
        & (df_filtered.period_int <= selected_period[1])
    ]
    fig_temp = px.line(
        df_filtered, x="period", y="TMK", color="year", title="Temperature"
    )
    fig_temp.update_layout(xaxis=dict(tickformat="%d-%b"))

    fig_press = px.line(df_filtered, x="period", y="PM", color="year", title="Pressure")
    fig_press.update_layout(xaxis=dict(tickformat="%d-%b"))
    fig_precip = px.bar(
        df_filtered, x="period", y="RSK", color="year", title="Precipitation"
    )
    fig_precip.update_layout(xaxis=dict(tickformat="%d-%b"))

    fig_cover = px.scatter(
        df_filtered, x="period", y="NM", color="year", title="Cloud Coverage",
    )
    fig_cover.update_layout(xaxis=dict(tickformat="%d-%b"))

    return fig_temp, fig_press, fig_precip, fig_cover


if __name__ == "__main__":
    app.run_server(debug=True)
