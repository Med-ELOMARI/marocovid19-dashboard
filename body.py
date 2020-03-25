# -*- coding: utf-8 -*-
import dash_table
import pandas as pd
from dash.dependencies import Input, Output, State
import dash_core_components as dcc
import dash_html_components as html
from plotly import graph_objs as go

from app import app

import plotly.express as px

from fields import (
    MODE_BAR_TIME_LINE_HIDES,
    MAPS_LIST,
    MODE_BAR_MAP_HIDES,
    QUARANTINE_DATE,
)


# return html Table with dataframe values
def df_to_table(df):
    return dash_table.DataTable(
        id="table",
        columns=[{"name": i, "id": i} for i in df.columns],
        data=df.to_dict("records"),
        style_cell={"textAlign": "left", "font_family": "Ubuntu", "font_size": "14px"},
        style_data={"whiteSpace": "normal", "height": "auto"},
        sort_action="native",
        column_selectable="single",
        sort_by=[dict(column_id=df.columns[-1],
                      direction='desc')]

    )


# returns top indicator div
def indicator(color, text, id_value, test=False):
    return html.Div(
        [
            html.P(id=id_value, className="indicator_value", style=dict(color=color)),
            html.P(text, className="twelve columns indicator_text", ),
        ],
        className="four columns indicator pretty_container",
    )


def preprocess(data, region_col, target):
    cords = pd.DataFrame.from_dict(data["regions"])
    regions = pd.DataFrame.from_dict(data["data"]["tab_json"])
    regions = (
        regions.set_index(region_col).join(cords.set_index("Region")).reset_index()
    )
    regions[target] = regions[target].astype("int32")
    return regions


# returns choropleth map figure based on status filter
def morocco_map(map, data):
    target = "Nombre de cas confirmés"
    regions = preprocess(data, "Région", target)

    fig = px.scatter_mapbox(
        regions,
        lat="Latitude",
        lon="Longitude",
        hover_name="Région",
        hover_data=[target],
        color=target,
        size=target,
        color_continuous_scale=["yellow", "orange", "red"],
        zoom=3.7,
        title="Regions Data",
    )
    fig.update_layout(mapbox_style=map)
    fig.update_layout(coloraxis_colorbar=dict(title="Infections", ))
    fig.update_layout(margin={"r": 0, "t": 0, "l": 0, "b": 0})
    return dict(data=[fig.data[0]], layout=fig.layout)


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
                    dcc.Tabs(id="tabs", value='tab-1', children=[
                        dcc.Tab(label='Map', value='tab-1'),
                        dcc.Tab(label='Table', value='tab-2'),
                    ], colors={
                        "border": "white",
                        "primary": "gray",
                        "background": "#e8e8e8"
                    }),
                    html.Div(id='tabs-content'),
                ],
            ),

            # html.Div(id="regions_table", className="row pretty_container table"),
        ],
    ),
]


# updates left indicator based on df updates
@app.callback(Output("update_time", "children"), [Input("data_json", "data")])
def time_update_callback(data_json):
    return dcc.Markdown("**Last Update : {}**".format(data_json["current_update"]))


# updates left indicator based on df updates
@app.callback(Output("left_indicator", "children"), [Input("data_json", "data")])
def left_indicator_callback(data_json):
    return dcc.Markdown(
        "**<sup>{}</sup>/<sub>{}</sub>**".format(
            data_json["data"]["Infected"], data_json["data"]["Infected"] + data_json["data"]["Tested"]
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


def make_line_graph(x, y, title, color):
    return go.Scatter(
        x=x,
        y=y,
        mode="lines+markers",
        marker=dict(size=3, line=dict(width=1), color=color),
        name=title,
    )


# update pie chart figure based on dropdown's value and df updates
@app.callback(
    Output("time_line", "figure"),
    [Input("data_json", "data"), Input("loader", "children")],
)
def time_line_callback(data, _):
    infected = [v["ConfirmedCases"] for _, v in data["raw"].items()]
    Died = [v["Fatalities"] for _, v in data["raw"].items()]
    dates = list(data["raw"].keys())
    infected_graph = make_line_graph(dates, infected, "Infected", "#fc8123")
    Died_graph = make_line_graph(dates, Died, "Died", "red")

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
        yaxis=dict(title="Counter (people)", ticklen=5, gridwidth=2, ),
        legend=dict(x=0, y=1),
        margin={"t": 0, "b": 0, "l": 50, "r": 0},
        shapes=[
            dict(
                type="line",
                xref="x1",
                yref="y1",
                x0=QUARANTINE_DATE,
                y0=0,
                x1=QUARANTINE_DATE,
                y1=infected[-1],
                line_width=2,
                line_dash="dashdot",
            ),
        ],
        annotations=[
            dict(
                x=QUARANTINE_DATE,
                y=infected[-1] * 2 / 3,
                xref="x",
                yref="y",
                text="Quarantine Started",
                showarrow=True,
                arrowhead=1,
                ax=-80,
                ay=-30,
            )
        ],
    )
    return dict(data=[infected_graph, Died_graph], layout=layout_comp)


@app.callback(Output('tabs-content', 'children'),
              [Input('tabs', 'value'), Input("data_json", "data")])
def render_content(tab, data):
    if tab == 'tab-1':
        return html.Div([
            html.P("Infection Per regions"),
            html.Div(
                className="two columns dd-styles",
                children=dcc.Dropdown(
                    id="maps_dropdown",
                    options=[
                        {
                            "label": "Map [" + map.replace("-", " ") + "]",
                            "value": map,
                        }
                        for map in MAPS_LIST
                    ],
                    value="carto-positron",
                    clearable=False,
                ),
            ), dcc.Graph(
                id="map",
                config={
                    "displaylogo": False,
                    "modeBarButtonsToRemove": MODE_BAR_MAP_HIDES,
                },
            ),
            dcc.Markdown(
                f"**Note :** There is **No** political intention behind the used maps ,I choosed _stamen-watercolor_  Because it doesn have borders :)"
            ),
        ])
    elif tab == 'tab-2':
        df = pd.DataFrame.from_dict(data["data"]["tab_json"])
        df.rename(
            columns={"Nombre de cas confirmés": "Confirmed Cases", "Région": "Province"},
            inplace=True,
        )
        df["Confirmed Cases"] = df["Confirmed Cases"].astype("int32")
        df = df.reindex(columns=list(df.columns)[::-1])
        return html.Div(children=[
            html.P("Infection Per regions"),
            df_to_table(df)
        ])
