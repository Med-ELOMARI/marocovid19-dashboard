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
    make_death_ratio_graph,
)


def get_layout(language: dict):
    layout = [
        html.Div(
            id="my_grid",
            children=[
                # hidden Div For loading
                html.Div(id="loader", style={"display": "none"}),
                html.Div(
                    className="row indicators",
                    children=[
                        indicator(
                            "#fc8123", language.get("Infected_Tested"), "left_indicator"
                        ),
                        indicator(
                            "#ff0000", language.get("Deaths"), "middle_indicator_1"
                        ),
                        indicator(
                            "#00cc96", language.get("Recovered"), "right_indicator"
                        ),
                        indicator(
                            "#dbd000",
                            language.get("Active Cases"),
                            "middle_indicator_2",
                        ),
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
                                dcc.Tab(label=language.get("Map"), value="tab-1"),
                                dcc.Tab(label=language.get("Table"), value="tab-2"),
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
                    id="prediction_area",
                    className="row pretty_container",
                    children=[
                        html.Div(
                            children=[
                                dcc.Dropdown(
                                    id="method_dropdown_menu",
                                    options=[
                                        {
                                            "label": language.get("pred_drop_2"),
                                            "value": "D_Ratio",
                                        },
                                        {
                                            "label": language.get("pred_drop_1"),
                                            "value": "GB_MODEL",
                                        },

                                        {
                                            "label": language.get("pred_drop_3"),
                                            "value": "NNK_MODEL",
                                        },
                                    ],
                                    value="D_Ratio",
                                    clearable=False,
                                ),
                                html.Div(
                                    id="deaths_ratio_input",
                                    children=[
                                        html.P(
                                            language.get("Mortality_Rate_input"),
                                            style={
                                                "width": "12",
                                                "display": "inline-block",
                                                "margin-left": "10px",
                                            },
                                        ),
                                        dcc.Input(
                                            id="deaths_ratio_input_box",
                                            value=1,
                                            type="number",
                                            min=0.01,
                                            max=100,
                                            step=0.01,
                                            style={
                                                "padding": "4px",
                                                "margin-left": "1vw",
                                            },
                                        ),
                                    ],
                                ),
                            ]
                        ),
                        dcc.Graph(
                            id="pred_graph",
                            config={
                                "displaylogo": False,
                                "modeBarButtonsToRemove": MODE_BAR_TIME_LINE_HIDES,
                            },
                        ),
                    ],
                ),
                html.Div(
                    id="testing_area", className="row pretty_container", children=[],
                ),
                html.Div(
                    id="sources",
                    className="row pretty_container",
                    children=[
                        dcc.Markdown(
                            open(
                                f"RESOURCES_{language.get('prefix')}.md",
                                encoding="utf-8",
                            ).read(),
                            dangerously_allow_html=True,
                        )
                    ],
                )
            ],
        ),
    ]
    return layout


# updates left indicator based on df updates
@app.callback(
    Output("deaths_ratio_input", "hidden"), [Input("method_dropdown_menu", "value")]
)
def deaths_ratio_input_box_callback(value):
    return value != "D_Ratio"


# updates left indicator based on df updates
@app.callback(
    Output("update_time", "children"),
    [Input("language_json", "data"), Input("data_json", "data")],
)
def time_update_callback(language_json, data_json):
    current_update = (
        datetime.strptime(data_json["current_update"], "%a %b %d %H:%M:%S %Y")
        if data_json
        else "Loading ..."
    )
    return dcc.Markdown(f"**{language_json.get('Update_message')} : {current_update}**")


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
    Output("pred_graph", "figure"),
    [
        Input("loader", "children"),
        Input("data_json", "data"),
        Input("method_dropdown_menu", "value"),
        Input("deaths_ratio_input_box", "value"),
        Input("language_json", "data"),
    ],
)
def prediction_area_callback(_, data_json, type, ratio, language):
    if type == "D_Ratio":
        return make_death_ratio_graph(ratio, data_json, language)
    elif type == "NNK_MODEL":
        # return make_prediction_graph("Keras",data_json)
        return dict(
            data=[],
            layout=dict(
                annotations=[
                    dict(
                        name="bg",
                        text=language.get("Soon"),
                        textangle=-30,
                        opacity=0.1,
                        font=dict(color="black", size=50),
                        xref="paper",
                        yref="paper",
                        x=0.5,
                        y=0.5,
                        showarrow=False,
                    )
                ]
            ),
        )
    else:
        return make_prediction_graph("GB_Predictor", data_json, language)


# update heat map figure based on dropdown's value and df updates
@app.callback(
    Output("testing_area", "children"),
    [
        Input("loader", "children"),
        Input("data_json", "data"),
        Input("language_json", "data"),
    ],
)
def prediction_area_callback(_, data_json, language):
    return testing_area_maker(DEFAULT_DROPDOWN_FIELDS, data_json, language)


@app.callback(
    Output("test_graph", "figure"),
    [
        Input("data_json", "data"),
        Input("testing_dropdown_menu", "value"),
        Input("language_json", "data"),
    ],
)
def testing_dropdown_menu_callback(data_json, search_value, language):
    return testing_area_maker(search_value, data_json, language, update=True)


# update pie chart figure based on dropdown's value and df updates
@app.callback(
    Output("time_line", "figure"),
    [
        Input("data_json", "data"),
        Input("loader", "children"),
        Input("language_json", "data"),
    ],
)
def time_line_callback(data, _, language):
    infected = get_field("ConfirmedCases", data["raw"])
    Died = get_field("Fatalities", data["raw"])
    Recovered = get_field("Recovered", data["raw"])
    dates = list(data["raw"].keys())
    graphs = [
        make_line_graph(dates, Recovered, language.get("Recovered"), "green"),
        make_line_graph(dates, infected, language.get("Infected"), "#fc8123"),
        make_line_graph(dates, Died, language.get("Deaths"), "red"),
    ]

    layout_comp = go.Layout(
        title={
            "text": language.get("Time_line_title"),
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
                x=0,
                y=1,
                buttons=list(
                    [
                        dict(count=7, label="Week", step="day", stepmode="backward"),
                        dict(count=1, label="Month", step="month", stepmode="backward"),
                        dict(label="All", step="all"),
                    ]
                ),
            ),
            rangeslider=dict(visible=True, autorange=True),
            type="date",
        ),
        yaxis=dict(title="People Counter", ticklen=5, gridwidth=2, ),
        legend=dict(
            x=0, y=1, orientation="v", itemsizing="constant", bgcolor="rgba(0,0,0,0)"
        ),
        margin={"t": 50, "b": 0, "l": 50, "r": 0},
    )
    return dict(data=graphs, layout=layout_comp)


@app.callback(
    Output("tabs-content", "children"),
    [
        Input("tabs", "value"),
        Input("data_json", "data"),
        Input("language_json", "data"),
    ],
)
def render_content(tab, data, language):
    if tab == "tab-1":
        return html.Div(children=make_map(language))
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
        return html.Div(
            children=[
                html.P(language.get("Infections_per_regions_table")),
                df_to_table(df),
            ]
        )
