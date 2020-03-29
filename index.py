import json

import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Output, Input, State

import body
import project_details
from Database import morocco
from app import app

server = app.server

app.layout = html.Div(
    [
        html.Div(
            className="row header",
            children=[
                html.Span(
                    className="app-title",
                    children=[
                        dcc.Markdown("**Maroc Covid-19**"),
                        html.Span(
                            id="subtitle",
                            children=dcc.Markdown(
                                "&nbsp Data , insights and Predictions"
                            ),
                            style={"font-size": "1.8rem", "margin-top": "15px"},
                        ),
                    ],
                ),
                html.Div(
                    id="update_time",
                    className="time_container",
                    style={
                        "font-size": "150%",
                        "grid-row": "1 / 2",
                        "grid-column": "3 / 7",
                    },
                ),
            ],
        ),
        dcc.Store(id="data_json"),  # in memory json Data
        dcc.Location(id="url", refresh=False),
        html.Div(id="body"),
        html.Link(
            href="https://use.fontawesome.com/releases/v5.2.0/css/all.css",
            rel="stylesheet",
        ),
        html.Link(
            href="https://fonts.googleapis.com/css?family=Dosis", rel="stylesheet"
        ),
        html.Link(
            href="https://fonts.googleapis.com/css?family=Open+Sans", rel="stylesheet"
        ),
        html.Link(
            href="https://fonts.googleapis.com/css?family=Ubuntu", rel="stylesheet"
        ),
        html.Footer(
            id="header",
            className="row header",
            children=[
                html.A(
                    dcc.Markdown("**Developed by Mohamed EL Omari**"),
                    href="https://elomari.ml",
                    target="_blank",
                    style={"padding-left": "5rem", "padding-right": "5rem"},
                ),
                html.A(
                    dcc.Markdown("**Project Details**"),
                    href="/project_details",
                    target="_blank",
                    style={"padding-right": "5rem"},
                ),
                html.A(
                    dcc.Markdown("**Github Repository**"),
                    href="https://github.com/Med-ELOMARI/marocovid19-dashboard",
                    target="_blank",
                    style={"padding-right": "5rem", "padding-left": "5rem"},
                ),
            ],
        ),
    ],
    className="row",
    style={
        # "background-image": 'url(/assets/header.png)',
        # "background-size": "cover",
        # "background-attachment": "fixed",
        # "background-position": "center",
        "background-color": "#28282a"
    },
)


@app.callback(Output("data_json", "data"), [Input("loader", "children")])
def update_fields(_):
    return morocco.get()
    # with open("data/my_data.json", "rb") as f:
    #     data = json.load(f)
    # return data["maroc"]


# Update the index
@app.callback(
    [Output("body", "children"), Output("mobile_body", "children")],
    [Input("url", "pathname")],
)
def display_page(pathname):
    if pathname == "/project_details":
        return project_details.layout, project_details.layout
    return body.layout, body.layout


@app.callback(
    Output("mobile_body", "style"),
    [Input("menu", "n_clicks")],
    [State("mobile_body", "style")],
)
def show_menu(n_clicks, tabs_style):
    if n_clicks:
        if tabs_style["display"] == "none":
            tabs_style["display"] = "flex"
        else:
            tabs_style["display"] = "none"
    return tabs_style


if __name__ == "__main__":
    app.run_server(debug=True, port=80)
