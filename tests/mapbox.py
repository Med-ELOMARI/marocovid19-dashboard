import json

import pandas as pd

import plotly.express as px
import firebase_admin
from firebase_admin import credentials

cred = credentials.Certificate("conf.json")  # conf.json not included in the repo

firebase_admin.initialize_app(
    cred, {"databaseURL": "https://covid19maroc-632de.firebaseio.com"}
)
# Import database module.
from firebase_admin import db

# Get a database reference to our blog.
morocco = db.reference("maroc")

# cities = pd.read_csv("covid-19-morocco-regions.csv")
# locs = cities[['Region', 'Latitude', 'Longitude']]
# locs.reset_index(drop=True)
# print(locs)
# locs.to_json("new.json", "records")

# with open("covid19maroc-632de-export.json") as json_file:
#     data = json.load(json_file)
data = morocco.get()


def preprocess(data, region_col, target):
    cords = pd.DataFrame.from_dict(data["regions"])
    regions = pd.DataFrame.from_dict(data["data"]["tab_json"])
    regions = (
        regions.set_index(region_col).join(cords.set_index("Region")).reset_index()
    )
    regions[target] = regions[target].astype("int32")
    return regions


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
    color_continuous_scale="Inferno",
    zoom=3.7,
    title="Regions Data",
)
fig.update_layout(mapbox_style="stamen-watercolor")
fig.update_layout(coloraxis_colorbar=dict(title="Infections",))
fig.update_layout(margin={"r": 0, "t": 0, "l": 0, "b": 0})
fig.show()
