import dash_core_components as dcc
import dash_html_components as html

with open("README.md", "r") as f:
    README = f.read()

README = README.replace("![](assets/images/Screenshot.png)", "")
README = README.replace("# Structure\n\n![](assets/images/structure.png)", "")
README = README.replace(
    "[![Deploy]",
    "Please Open the project in github then click the button from there \n\n[![Deploy]",
)
layout = html.Div(
    className="pretty_container",
    children=[
        html.Img(
            id="image_size", className="image_size", src="assets/images/structure.png"
        ),
        dcc.Markdown(README),
    ],
)
