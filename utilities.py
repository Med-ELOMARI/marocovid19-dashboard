# -*- coding: utf-8 -*-
from datetime import datetime

import dash_html_components as html
import dash_table
import pandas as pd
import dash_core_components as dcc
import plotly

import plotly.express as px
from plotly import graph_objs as go

from fields import (
    MODE_BAR_TIME_LINE_HIDES,
    DEFAULT_DROPDOWN_FIELDS,
    MODE_BAR_MAP_HIDES,
    MAPS_LIST,
)

COVID_19_TESTS_COUNTRY = pd.read_csv("data/covid-19-tests-country.csv")
COVID_19_TESTS_COUNTRY = COVID_19_TESTS_COUNTRY.rename(
    columns={"Entity": "Country", "Total COVID-19 tests": "Tests"}
)
COVID_19_TESTS_COUNTRY["Date"] = COVID_19_TESTS_COUNTRY["Date"].apply(
    lambda x: datetime.strptime(str(x), "%b %d, %Y").strftime("%Y/%m/%d")
)


def get_field(field, data):
    return [v[field] for _, v in data.items()]


def convert_to_date(date, _from="%a %b %d %H:%M:%S %Y", to="%Y-%m-%d"):
    """
    ctime to %Y-%m-%d
    :param date:
    :return: datetime object
    """
    return datetime.strptime(str(date), _from).strftime(to)


def make_line_graph(x, y, title, color, dash=False):
    return go.Scatter(
        x=x,
        y=y,
        mode="lines+markers",
        marker=dict(size=3, line=dict(width=1), color=color),
        name=title,
        line_dash="dash" if dash else None,
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
        sort_by=[dict(column_id=df.columns[-1], direction="desc")],
    )


# returns top indicator div
def indicator(color, text, id_value, test=False):
    return html.Div(
        [
            html.P(id=id_value, className="indicator_value", style=dict(color=color)),
            html.P(text, className="twelve columns indicator_text",),
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
    fig.update_layout(coloraxis_colorbar=dict(title="Infections",))
    fig.update_layout(margin={"r": 0, "t": 0, "l": 0, "b": 0})
    return dict(data=[fig.data[0]], layout=fig.layout)


def make_prediction_graph(data: dict):
    preds: dict = data["predictions"]["GB_Predictor"]
    graphs = [
        make_line_graph(
            x=list(preds.keys()),
            y=list(preds.values()),
            title="Prediction",
            color="purple",
            dash=True,
        ),
        make_line_graph(
            x=list(data["raw"].keys()),
            y=get_field("ConfirmedCases", data["raw"]),
            title="Current Infected",
            color="#fc8123",
        ),
    ]
    layout_comp = go.Layout(
        title={
            "text": f"Predictions of infected People ( Till {list(preds.keys())[-1]} )",
            "y": 0.9,
            "x": 0.5,
            "xanchor": "center",
            "yanchor": "bottom",
        },
        hovermode="closest",
        xaxis=dict(title="Time", ticklen=5, zeroline=False, gridwidth=2, type="date",),
        yaxis=dict(title="People Counter", ticklen=5, gridwidth=2,),
        legend=dict(orientation="h", itemsizing="constant"),
    )

    return [
        dcc.Graph(
            id="pred_graph",
            figure=dict(data=graphs, layout=layout_comp),
            config={
                "displaylogo": False,
                "modeBarButtonsToRemove": MODE_BAR_TIME_LINE_HIDES,
            },
        )
    ]


def testing_area_maker(selection, data, update=False):
    df = COVID_19_TESTS_COUNTRY
    df = df.append(
        {
            "Country": "Morocco",
            "Tests": data["data"]["Tested"]+data["data"]["Infected"],
            "Date": convert_to_date(data["current_update"], to="%Y/%m/%d"),
        },
        ignore_index=True,
    )
    countries = df["Country"].unique()

    df = df[df["Country"].isin(selection)]

    fig = px.bar(
        df,
        y="Country",
        x="Tests",
        orientation="h",
        hover_name="Country",
        hover_data=["Date"],
        text="Tests",
        labels=["Date"],
        title={
            "text": "Testing for COVID-19",
            "xanchor": "center",
            "yanchor": "bottom",
        },
    )
    fig.update_layout(yaxis={"categoryorder": "total ascending"})
    fig.update_layout(margin={"r": 0, "t": 0, "l": 0, "b": 0})

    if update:
        return dict(data=[fig.data[0]], layout=fig.layout)

    return [
        dcc.Dropdown(
            id="testing_dropdown_menu",
            options=[{"label": c, "value": c} for c in countries],
            multi=True,
            value=DEFAULT_DROPDOWN_FIELDS,
        ),
        dcc.Graph(
            id="test_graph",
            figure=dict(data=[fig.data[0]], layout=fig.layout),
            style={"height": "53vh"},
            config={
                "displaylogo": False,
                "modeBarButtonsToRemove": MODE_BAR_TIME_LINE_HIDES,
            },
        ),
    ]


def make_map():
    return [
        html.P("Infection Per regions"),
        html.Div(
            className="two columns dd-styles",
            children=dcc.Dropdown(
                id="maps_dropdown",
                options=[
                    {"label": "Map [" + map.replace("-", " ") + "]", "value": map,}
                    for map in MAPS_LIST
                ],
                value="carto-positron",
                clearable=False,
            ),
        ),
        dcc.Graph(
            id="map",
            config={
                "displaylogo": False,
                "modeBarButtonsToRemove": MODE_BAR_MAP_HIDES,
            },
        ),
        dcc.Markdown(
            f"**Note :** There is **No** political intention behind the used maps ,I choosed _stamen-watercolor_  Because it doesn have borders :)"
        ),
    ]
