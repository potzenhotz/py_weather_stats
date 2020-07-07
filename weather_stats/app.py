import os
import dash
import dash_html_components as html
import dash_core_components as dcc
import plotly.express as px
import plotly.graph_objects as go
import weather_data as wd


ws = wd.weather_station()
df_weather = ws.get_weather_df()
df_temp = ws.get_temp_df()

external_stylesheets = ["https://codepen.io/chriddyp/pen/bWLwgP.css"]

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

# fig = px.line(df_temp, x="period", y=2000,)
# fig.add_scatter(df_temp, x="period", y=2001, mode="lines")

fig = px.line(df_weather, x="period", y="PM", color="year")
fig.update_layout(xaxis=dict(tickformat="%d-%b"))

# years_list = df_temp.columns.tolist()
# years_list.pop(0)
# fig = go.Figure()
# for year in years_list:
#    fig.add_trace(
#        go.Scatter(x=df_temp["period"], y=df_temp[year], mode="lines", name=year,)
#    )


app.layout = html.Div(
    children=[
        html.H1(children="Hello Dash"),
        html.Div(
            children="""
        Dash: A web application framework for Python.
    """
        ),
        dcc.Graph(id="example-graph", figure=fig),
    ]
)


if __name__ == "__main__":
    app.run_server(debug=True)
