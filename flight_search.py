import requests
from datetime import datetime as dt
import os
from pprint import pprint
import json


kiwi_api = os.environ.get("kiwi_api")
kiwi_endpoint = "https://api.tequila.kiwi.com"


headers = {
    "apikey": kiwi_api,
}


# This class is responsible for talking to the Flight Search API.
class FlightSearch:
    def __init__(self):
        self.city_codes = {}
        self.final = {}

    # gets the city iata codes and updates them in the sheet (gets called from DataManager)
    def get_city_codes(self, city):
        self.query_params = {"term": f"{city}", "limit": "1"}
        r = requests.get(
            f"{kiwi_endpoint}/locations/query",
            params=self.query_params,
            headers=headers,
        )
        data = r.json()
        city_code = data["locations"][0]["code"]
        return city_code

    def manual_search_flights(
        self, start, destination, date_from1, date_from2, start_nights, end_nights
    ):
        self.list_of_airlines = ["TAM", "GLO", "AZU"]
        self.request_params = {
            "fly_from": start,
            "fly_to": destination,
            "date_from": date_from1,
            "date_to": date_from2,
            "return_from": start_nights,
            "return_to": end_nights,
            "nights_in_dst_from": "8",
            "nights_in_dst_to": "10",
            "ret_from_diff_city": "false",
            "ret_to_diff_city": "false",
            "adults": "1",
            "selected_cabins": "M",
            "adult_hold_bag": "0",
            "adult_hand_bag": "0",
            "curr": "BRL",
            "max_stopovers": "0",
            "ret_from_diff_airport": "0",
            "ret_to_diff_airport": "0",
            "vehicle_type": "aircraft",
            "limit": "500",
            "partner_market": "us",
            "sort": "price",
        }
        r = requests.get(
            url=f"{kiwi_endpoint}/v2/search",
            headers=headers,
            params=self.request_params,
        )
        r.raise_for_status()
        flight_data = r.json()
        with open("data.json", "w") as f:
            f.write(json.dumps(flight_data))

    def automatic_search_sheet(self, destination, dates):
        self.request_params = {
            "fly_from": "SKP",
            "fly_to": destination,
            "date_from": dates[0],
            "date_to": dates[1],
            "nights_in_dst_from": "7",
            "nights_in_dst_to": "28",
            "ret_from_diff_city": "false",
            "ret_to_diff_city": "false",
            "adults": "1",
            "one_for_city": 1,
            "selected_cabins": "M",
            # if you want to see the prices of the tickets with baggage,update the two parameters below
            "adult_hold_bag": "0",
            "adult_hand_bag": "0",
            "curr": "EUR",
            "max_stopovers": "0",
            "ret_from_diff_airport": "0",
            "ret_to_diff_airport": "0",
            "vehicle_type": "aircraft",
            "partner_market": "mk",
            "sort": "price",
        }
        r = requests.get(
            url=f"{kiwi_endpoint}/v2/search",
            headers=headers,
            params=self.request_params,
        )
        r.raise_for_status()
        final_data = r.json()
        with open("data2.json", "w") as f:
            f.write(json.dumps(final_data))
        return final_data
