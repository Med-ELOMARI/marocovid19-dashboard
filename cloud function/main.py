from scrap import Scrapper, convert_to_date

from Database import morocco

url = "http://www.covidmaroc.ma/Pages/AccueilAR.aspx"
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:47.0) Gecko/20100101 Firefox/47.0"
}
date_selector = "#WebPartWPQ1 > div:nth-child(1) > div:nth-child(1) > table:nth-child(1) > tbody:nth-child(1) > tr:nth-child(1) > td:nth-child(1) > p:nth-child(1) > font:nth-child(1)"
Tested_selector = "#WebPartWPQ1 > div:nth-child(1) > div:nth-child(1) > table:nth-child(1) > tbody:nth-child(1) > tr:nth-child(2) > td:nth-child(3) > p:nth-child(1)"
Infected_selector = "#WebPartWPQ1 > div:nth-child(1) > div:nth-child(1) > table:nth-child(1) > tbody:nth-child(1) > tr:nth-child(2) > td:nth-child(2) > p:nth-child(1)"
Recovered_Died_selector = "#WebPartWPQ1 > div:nth-child(1) > div:nth-child(1) > table:nth-child(1) > tbody:nth-child(1) > tr:nth-child(2) > td:nth-child(1) > p:nth-child(1)"
table_selector = {"class": "ms-rteTable-6"}


def function(request):
    """Responds to any HTTP request.
    Args:
        request (flask.Request): HTTP request object.
    Returns:
        The response text or any set of values that can be turned into a
        Response object using
        `make_response <http://flask.pocoo.org/docs/1.0/api/#flask.Flask.make_response>`.
    """

    sc = Scrapper(
        url,
        headers,
        date_selector,
        Tested_selector,
        Infected_selector,
        Recovered_Died_selector,
        table_selector,
    )
    data = sc.get_data()  # Scrapped Data
    morocco_data = morocco.get()  # snap from existing Data
    current_update = morocco_data["current_update"]
    if current_update != data["date"]:
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
        return f"OK , Updated to {data['date']}"
    else:
        return "Noting to Update"


# if __name__ == "__main__":
#     sc = Scrapper(
#         url,
#         headers,
#         date_selector,
#         Tested_selector,
#         Infected_selector,
#         Recovered_Died_selector,
#         table_selector,
#     )
#     data = sc.get_data()  # Scrapped Data
