import json

from dash.dependencies import Output, Input, State
import dash_core_components as dcc
import dash_html_components as html
import body
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
                            children=dcc.Markdown("&nbsp Data , insights and Predictions"),
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
    ],
    className="row landscape_switcher",
    style={
        # "margin": "0%",
        # "background-image": 'url(/assets/header.png)',
        # "background-size": "cover",
        # "background-attachment": "fixed",
        # "background-position": "center"
        "background-color": "#e8e8e8"
    },
)


@app.callback(Output("data_json", "data"), [Input("loader", "children")])
def update_fields(_):
    return morocco.get()


# Update the index
@app.callback(
    [Output("body", "children"), Output("mobile_body", "children"), ],
    [Input("url", "pathname")],
)
def display_page(pathname):
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
