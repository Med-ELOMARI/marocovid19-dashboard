import hashlib

from gb_predictor import GB_Predictor
from scrap import Scrapper, convert_to_date

from Database import morocco

from random_user_agent.user_agent import UserAgent
from random_user_agent.params import SoftwareName, OperatingSystem

software_names = [SoftwareName.CHROME.value]
operating_systems = [OperatingSystem.WINDOWS.value, OperatingSystem.LINUX.value]

user_agent_rotator = UserAgent(software_names=software_names, operating_systems=operating_systems, limit=100)

url = "http://www.covidmaroc.ma/Pages/AccueilAR.aspx"
date_selector = "#WebPartWPQ1 > div.ms-rtestate-field > div:nth-child(1) > table > tbody > tr:nth-child(1) > td > p"
Tested_selector = "#WebPartWPQ1 > div:nth-child(1) > div:nth-child(1) > table:nth-child(1) > tbody:nth-child(1) > tr:nth-child(2) > td:nth-child(3) > p:nth-child(1)"
Infected_selector = "#WebPartWPQ1 > div:nth-child(1) > div:nth-child(1) > table:nth-child(1) > tbody:nth-child(1) > tr:nth-child(2) > td:nth-child(2) > p:nth-child(1)"
Recovered_Died_selector = "#WebPartWPQ1 > div:nth-child(1) > div:nth-child(1) > table:nth-child(1) > tbody:nth-child(1) > tr:nth-child(2) > td:nth-child(1) > p:nth-child(1)"
Recovered_selector = ".ms-rteForeColor-6"
Died_selector = ".ms-rteThemeForeColor-9-4"
table_selector = {"class": "ms-rteTable-6"}


def update_predictions():
    try:
        data = morocco.get()
        p = GB_Predictor(data["raw"], "model.pkl")
        r = p.predict(10, as_df=False)
        morocco.child("predictions").child("GB_Predictor").set(r)
        return "Updated Predictions"
    except Exception as e:
        return f"Error {str(e)}"


def get_hash(data):
    return hashlib.md5(str(data).encode("utf-8")).hexdigest()


def function(request):
    """Responds to any HTTP request.
    Args:
        request (flask.Request): HTTP request object.
    Returns:
        The response text or any set of values that can be turned into a
        Response object using
        `make_response <http://flask.pocoo.org/docs/1.0/api/#flask.Flask.make_response>`.
    """
    headers = {
        "User-Agent": user_agent_rotator.get_random_user_agent()
    }

    sc = Scrapper(
        url,
        headers,
        date_selector,
        Tested_selector,
        Infected_selector,
        Recovered_Died_selector,
        table_selector,
        Recovered_selector,
        Died_selector,
    )
    data = sc.get_data()  # Scrapped Data
    morocco_data = morocco.get()  # snap from existing Data
    new_hash = get_hash(
        str(data['Tested'])
        + str(data['Died'])
        + str(data['Infected'])
        + str(data['Recovered'])
    )
    old_hash = get_hash(
        str(morocco_data["data"]["Tested"])
        + str(morocco_data["data"]["Died"])
        + str(morocco_data["data"]["Infected"])
        + str(morocco_data["data"]["Recovered"])
    )
    if new_hash != old_hash:
        morocco.update(dict(current_update=data["date"]))
        morocco.child("history").update(
            {morocco_data["data"]["date"]: morocco_data["data"]}
        )
        morocco.update(dict(data=data))
        morocco.child("raw").update(
            {
                convert_to_date(data["date"]): {
                    "ConfirmedCases": data["Infected"],
                    "Fatalities": data["Died"],
                    "Recovered": data["Recovered"],
                    "Tested": data["Tested"],
                }
            }
        )
        msg = update_predictions()
        return f"OK , Updated to {data['date']}  | Prediction :{msg}"
    else:
        return "Noting to Update"


#
if __name__ == "__main__":
    print(function(""))
# if __name__ == "__main__":
#     data = morocco.get()
#     p = GB_Predictor(data["raw"], "model.pkl")
#     r = p.predict(10, as_df=False)

#
# if __name__ == "__main__":
#     sc = Scrapper(
#         url,
#         headers,
#         date_selector,
#         Tested_selector,
#         Infected_selector,
#         Recovered_Died_selector,
#         table_selector,
#         Recovered_selector,
#         Died_selector,
#     )
#     print(sc.get_data())
