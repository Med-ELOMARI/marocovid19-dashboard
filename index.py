import json

import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Output, Input, State
from flask import make_response, jsonify

import body
import project_details
from Database import morocco
from app import app
from languages import English, Arabic

server = app.server

app.layout = html.Div(
    [
        dcc.Location(id="url", refresh=False),
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
                html.A(
                    id="language",
                    children=html.Button("العربية", id="language_btn"),
                    href="/Arabic",
                    style={"margin-left": "1vh"},
                ),
            ],
        ),
        dcc.Store(id="data_json"),  # in memory json Data
        dcc.Store(id="language_json", data=English),  # in session json Data
        # dcc.Store(id="language_json", type="session"),  # in session json Data
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


@app.callback(
    [
        Output("language_btn", "children"),
        Output("language", "href"),
        Output("language_json", "data"),
    ],
    [Input("url", "pathname")],
)
def update_output(pathname):
    if pathname == "/Arabic":
        # Button text - href - json to use in display
        return "English", "/", Arabic
    else:
        # Button text - href - json to use in display
        return "العربية", "/Arabic", English


@app.callback(Output("data_json", "data"), [Input("loader", "children")])
def update_fields(_):
    return morocco.get()


# Update the index
@app.callback(
    [Output("body", "children"), Output("mobile_body", "children")],
    [Input("url", "pathname"), Input("language_json", "data")],
)
def display_page(pathname, language_json):
    if pathname == "/project_details":
        return project_details.layout, project_details.layout
    else:
        return body.get_layout(language_json), body.get_layout(language_json)


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


@server.route('/wakeup')
def wakeup():
    """
    a work around to wake up the server each 30 minutes by an external Cron job
    :return:
    """
    return make_response(jsonify(dict(status=True)), 200)


if __name__ == "__main__":
    app.run_server(debug=True, port=80)
