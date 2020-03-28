import dash

app = dash.Dash(
    __name__, meta_tags=[{"name": "viewport", "content": "width=device-width"}],
)

app.title = "Maroc Covid19"
app.config.suppress_callback_exceptions = True
# app.scripts.config.serve_locally = False
# app.scripts.append_script({"external_url": "https://cdn.plot.ly/plotly-locale-ar-latest.js"})
