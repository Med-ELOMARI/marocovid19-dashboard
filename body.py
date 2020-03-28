# -*- coding: utf-8 -*-
from datetime import datetime

import dash_core_components as dcc
import dash_html_components as html
import pandas as pd
from dash.dependencies import Input, Output
from plotly import graph_objs as go

from app import app
from fields import MODE_BAR_TIME_LINE_HIDES, DEFAULT_DROPDOWN_FIELDS
from utilities import (
    indicator,
    morocco_map,
    df_to_table,
    make_line_graph,
    get_field,
    make_prediction_graph,
    testing_area_maker,
    make_map,
)

layout = [
    html.Div(
        id="my_grid",
        children=[
            # hidden Div For loading
            html.Div(id="loader", style={"display": "none"}),
            html.Div(
                className="row indicators",
                children=[
                    indicator("#fc8123", "Infected/Tested", "left_indicator"),
                    indicator("#ff0000", "Died", "middle_indicator_1"),
                    indicator("#00cc96", "Recovered", "right_indicator"),
                    indicator("#dbd000", "Active Cases", "middle_indicator_2"),
                ],
            ),
            html.Div(
                id="time_line_container",
                className="time_line pretty_container",
                children=[
                    dcc.Graph(
                        id="time_line",
                        config={
                            "displaylogo": False,
                            "modeBarButtonsToRemove": MODE_BAR_TIME_LINE_HIDES,
                        },
                    ),
                ],
            ),
            html.Div(
                id="regions_map_data",
                className="chart_div pretty_container",
                children=[
                    dcc.Tabs(
                        id="tabs",
                        value="tab-1",
                        children=[
                            dcc.Tab(label="Map", value="tab-1"),
                            dcc.Tab(label="Table", value="tab-2"),
                        ],
                        colors={
                            "border": "white",
                            "primary": "gray",
                            "background": "#e8e8e8",
                        },
                    ),
                    html.Div(id="tabs-content"),
                ],
            ),
            html.Div(
                id="prediction_area", className="row pretty_container", children=[],
            ),
            html.Div(id="testing_area", className="row pretty_container", children=[],),
        ],
    ),
]


# updates left indicator based on df updates
@app.callback(Output("update_time", "children"), [Input("data_json", "data")])
def time_update_callback(data_json):
    current_update = datetime.strptime(
        data_json["current_update"], "%a %b %d %H:%M:%S %Y"
    )
    return dcc.Markdown(f"**Last Update : {current_update}**")


# updates left indicator based on df updates
@app.callback(Output("left_indicator", "children"), [Input("data_json", "data")])
def left_indicator_callback(data_json):
    return dcc.Markdown(
        "**<sup>{}</sup>/<sub>{}</sub>**".format(
            data_json["data"]["Infected"],
            data_json["data"]["Infected"] + data_json["data"]["Tested"],
        ),
        dangerously_allow_html=True,
        style=dict(sub={"color": "blue"}),
    )


# updates middle indicator based on df updates
@app.callback(Output("middle_indicator_1", "children"), [Input("data_json", "data")])
def middle_indicator_1_callback(data_json):
    return dcc.Markdown("**{}**".format(data_json["data"]["Died"]))


# updates middle indicator based on df updates
@app.callback(Output("middle_indicator_2", "children"), [Input("data_json", "data")])
def middle_indicator_2_callback(data_json):
    return dcc.Markdown(
        "**{}**".format(
            data_json["data"]["Infected"]
            - data_json["data"]["Died"]
            - data_json["data"]["Recovered"]
        )
    )


# updates right indicator based on df updates
@app.callback(Output("right_indicator", "children"), [Input("data_json", "data")])
def right_indicator_callback(data_json):
    return dcc.Markdown("**{}**".format(data_json["data"]["Recovered"]))


# update heat map figure based on dropdown's value and df updates
@app.callback(
    Output("map", "figure"),
    [Input("maps_dropdown", "value"), Input("data_json", "data")],
)
def map_callback(map, data_json):
    return morocco_map(map, data_json)


# update heat map figure based on dropdown's value and df updates
@app.callback(
    Output("prediction_area", "children"),
    [Input("loader", "children"), Input("data_json", "data")],
)
def prediction_area_callback(_, data_json):
    return make_prediction_graph(data_json)


# update heat map figure based on dropdown's value and df updates
@app.callback(
    Output("testing_area", "children"),
    [Input("loader", "children"), Input("data_json", "data")],
)
def prediction_area_callback(_, data_json):
    return testing_area_maker(DEFAULT_DROPDOWN_FIELDS, data_json)


@app.callback(
    Output("test_graph", "figure"),
    [Input("data_json", "data"), Input("testing_dropdown_menu", "value")],
)
def testing_dropdown_menu_callback(data_json, search_value):
    return testing_area_maker(search_value, data_json, update=True)


# update pie chart figure based on dropdown's value and df updates
@app.callback(
    Output("time_line", "figure"),
    [Input("data_json", "data"), Input("loader", "children")],
)
def time_line_callback(data, _):
    infected = get_field("ConfirmedCases", data["raw"])
    Died = get_field("Fatalities", data["raw"])
    Recovered = get_field("Recovered", data["raw"])
    dates = list(data["raw"].keys())

    graphs = [
        make_line_graph(dates, Recovered, "Recovered", "green"),
        make_line_graph(dates, infected, "Infected", "#fc8123"),
        make_line_graph(dates, Died, "Died", "red"),
    ]

    layout_comp = go.Layout(
        title={
            "text": "Time Line of Infected and Died",
            "y": 0.9,
            "x": 0.5,
            "xanchor": "center",
            "yanchor": "bottom",
        },
        hovermode="closest",
        xaxis=dict(
            title="Time",
            ticklen=5,
            zeroline=False,
            gridwidth=2,
            range=[dates[-22], dates[-1]],
            rangeselector=dict(
                buttons=list(
                    [
                        dict(count=7, label="Week", step="day", stepmode="backward"),
                        dict(count=1, label="Month", step="month", stepmode="backward"),
                        dict(step="all"),
                    ]
                )
            ),
            rangeslider=dict(visible=True, autorange=True),
            type="date",
        ),
        yaxis=dict(title="People Counter", ticklen=5, gridwidth=2,),
        legend=dict(orientation="h", itemsizing="constant"),
        margin={"t": 0, "b": 0, "l": 50, "r": 0},
    )
    return dict(data=graphs, layout=layout_comp)


@app.callback(
    Output("tabs-content", "children"),
    [Input("tabs", "value"), Input("data_json", "data")],
)
def render_content(tab, data):
    if tab == "tab-1":
        return html.Div(children=make_map())
    elif tab == "tab-2":
        df = pd.DataFrame.from_dict(data["data"]["tab_json"])
        df.rename(
            columns={
                "Nombre de cas confirmés": "Confirmed Cases",
                "Région": "Province",
            },
            inplace=True,
        )
        df["Confirmed Cases"] = df["Confirmed Cases"].astype("int32")
        df = df.reindex(columns=list(df.columns)[::-1])
        return html.Div(children=[html.P("Infection Per regions"), df_to_table(df)])
