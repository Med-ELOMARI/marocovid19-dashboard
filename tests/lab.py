import json
import pandas as pd
import plotly.graph_objects as go
import numpy as np

with open("covid19maroc-632de-export.json") as json_file:
    data = json.load(json_file)
data = pd.DataFrame.from_dict(data)
cols_reg = data.select_dtypes(
    include=[np.object]
).columns  # this and the next line remove french accents from region names
data[cols_reg] = data[cols_reg].apply(lambda x: x.str.normalize("NFKD").str)
print(data)
#
# df = pd.read_csv(
#     "https://raw.githubusercontent.com/plotly/datasets/master/2011_us_ag_exports.csv"
# )
# graph = go.Choropleth(
#     locations=df["code"],  # Spatial coordinates
#     z=df["total exports"].astype(float),  # Data to be color-coded
#     locationmode="country names",  # set of locations match entries in `locations`
#     colorscale="Reds",
#     colorbar_title="Millions USD",
# )
#
# fig = go.Figure(dict(
#     data=[graph],
#     layout={
#         "title_text": "2011 US Agriculture Exports by State",
#         "geo_scope": "africa",
#     },
# ))
# fig.show()

# def make_line_graph(x, y, title, color):
#     return go.Scatter(
#         x=x,
#         y=y,
#         mode="lines+markers",
#         marker=dict(size=8, line=dict(width=1), color=color),
#         name=title,
#     )
#
#
# infected = [v["ConfirmedCases"] for _, v in data["raw"].items()]
# Died = [v["Fatalities"] for _, v in data["raw"].items()]
# raw_data = list(data["raw"].keys())
# infected_graph = make_line_graph(raw_data, infected, "Infected", "blue")
# Died_graph = make_line_graph(raw_data, Died, "Died", "red")
# layout_comp = go.Layout(
#     title="Infected - Died",
#     hovermode="closest",
#     xaxis=dict(title="Time", ticklen=5, zeroline=False, gridwidth=2,),
#     yaxis=dict(title="Counter (people)", ticklen=5, gridwidth=2,),
# )
# fig = go.Figure(data=[infected_graph, Died_graph], layout=layout_comp)
# fig.show()
