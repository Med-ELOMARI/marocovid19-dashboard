# -*- coding: utf-8 -*-
from datetime import datetime

import dash_html_components as html
import dash_table
import pandas as pd
import dash_core_components as dcc

import plotly.express as px
from plotly import graph_objs as go

from fields import (
    MODE_BAR_TIME_LINE_HIDES,
    DEFAULT_DROPDOWN_FIELDS,
    MODE_BAR_MAP_HIDES,
    MAPS_LIST,
    QUARANTINE_DATE,
)

COVID_19_TESTS_COUNTRY = pd.read_csv("data/covid-19-tests-country.csv")
COVID_19_TESTS_COUNTRY = COVID_19_TESTS_COUNTRY.rename(
    columns={"Entity": "Country", "Total COVID-19 tests": "Tests"}
)
COVID_19_TESTS_COUNTRY["Date"] = COVID_19_TESTS_COUNTRY["Date"].apply(
    lambda x: datetime.strptime(str(x), "%b %d, %Y").strftime("%Y/%m/%d")
)

NEW_DF = pd.read_csv("data/full-list-total-tests-for-covid-19.csv")

NEW_DF = NEW_DF.rename(
    columns={"Entity": "Country", "Cumulative total tests": "Tests"}
)
NEW_DF = NEW_DF.groupby(["Country"]).sum()

COVID_19_TESTS_COUNTRY.append(NEW_DF)


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
        # legend=dict(bgcolor="rgba(0,0,0,0)")
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


def make_death_ratio_graph(ratio: int, data: dict, language: dict):
    deaths = get_field("Fatalities", data["raw"])
    calculated_infections = [d * 100 / ratio for d in deaths]
    y = get_field("ConfirmedCases", data["raw"])
    graphs = [
        make_line_graph(
            x=list(data["raw"].keys()),
            y=y,
            title=language.get("Current Infected"),
            color="#fc8123",
        ),
        make_line_graph(
            x=list(data["raw"].keys()),
            y=calculated_infections,
            title=f"{language.get('Calculated With Ratio')}({ratio}%)",
            color="navy",
        ),
    ]

    layout_comp = go.Layout(
        title={
            "text": f"{language.get('Estimation_title')} ({ratio}%)",
            "xanchor": "center",
            "yanchor": "bottom",
        },
        hovermode="closest",
        xaxis=dict(
            title=language.get("Time"),
            ticklen=5,
            zeroline=False,
            gridwidth=2,
            type="date",
        ),
        yaxis=dict(title=language.get("People Counter"), ticklen=5, gridwidth=2, ),
        legend=dict(orientation="h", itemsizing="constant", bgcolor="rgba(0,0,0,0)"),
        shapes=[
            dict(
                type="line",
                xref="x1",
                yref="y1",
                x0=QUARANTINE_DATE,
                y0=0,
                x1=QUARANTINE_DATE,
                y1=calculated_infections[-1],
                line_width=2,
                line_dash="dashdot",
            ),
        ],
        annotations=[
            dict(
                x=QUARANTINE_DATE,
                y=calculated_infections[-1] * 2 / 3,
                xref="x",
                yref="y",
                text=language.get("Quarantine Started"),
                showarrow=True,
                arrowhead=1,
                ax=-80,
                ay=-30,
            )
        ],
        margin={"r": 0, "l": 50, "t": 50, "b": 50},
    )

    return dict(data=graphs, layout=layout_comp)


def make_prediction_graph(predictions: str, data: dict, language: dict):
    preds: dict = data["predictions"][predictions]
    graphs = [
        make_line_graph(
            x=list(preds.keys()),
            y=list(preds.values()),
            title=language.get("Prediction"),
            color="purple",
            dash=True,
        ),
        make_line_graph(
            x=list(data["raw"].keys()),
            y=get_field("ConfirmedCases", data["raw"]),
            title=language.get("Current Infected"),
            color="#fc8123",
        ),
    ]

    layout_comp = go.Layout(
        title={
            "text": f"{language.get('predicition_graph_title')} {list(preds.keys())[-1]} )",
            "xanchor": "center",
            "yanchor": "bottom",
        },
        hovermode="closest",
        legend=dict(
            x=0, y=1, orientation="v", itemsizing="constant", bgcolor="rgba(0,0,0,0)"
        ),
        xaxis=dict(
            title=language.get("Time"),
            ticklen=5,
            zeroline=False,
            gridwidth=2,
            type="date",
        ),
        yaxis=dict(title=language.get("People Counter"), ticklen=5, gridwidth=2, ),
        shapes=[
            dict(
                type="line",
                xref="x1",
                yref="y1",
                x0=QUARANTINE_DATE,
                y0=0,
                x1=QUARANTINE_DATE,
                y1=list(preds.values())[-1],
                line_width=2,
                line_dash="dashdot",
            ),
        ],
        annotations=[
            dict(
                x=QUARANTINE_DATE,
                y=list(preds.values())[-1] * 2 / 3,
                xref="x",
                yref="y",
                text=language.get("Quarantine Started"),
                showarrow=True,
                arrowhead=1,
                ax=-80,
                ay=-30,
            )
        ],
        margin={"r": 0, "l": 50, "t": 50, "b": 50},
    )
    return dict(data=graphs, layout=layout_comp)


def testing_area_maker(
        selection, data, language, update=False,
):
    df = COVID_19_TESTS_COUNTRY
    df = df.append(
        {
            "Country": "Morocco",
            "Tests": data["data"]["Tested"] + data["data"]["Infected"],
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
        title={"text": language.get("Testing_title"), },
    )
    fig.update_layout(
        xaxis=dict(title=language.get("Tests_per_country")),
        yaxis=dict(
            title=language.get("Countries"),
            ticklen=5,
            gridwidth=2,
            categoryorder="total ascending",
        ),
        margin={"r": 0, "t": 0, "l": 0, "b": 0},
    )

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
        dcc.Markdown(
            "**Note:** There are substantial differences across countries in terms of the units, whether or not all labs are included, Details for each country can be found at [link](https://ourworldindata.org/covid-testing)")
    ]


def make_map(language):
    return [
        dcc.Markdown(f"{language.get('Choose_map')}:"),
        html.Div(
            className="two columns dd-styles",
            children=dcc.Dropdown(
                id="maps_dropdown",
                options=[
                    {"label": "Map [" + map.replace("-", " ") + "]", "value": map, }
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
        dcc.Markdown(f"{language.get('note')}"),
    ]
