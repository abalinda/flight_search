import requests
import json
from unidecode import unidecode
from pprint import pprint
from datetime import datetime as dt
from flight_search import FlightSearch

SHEET_ENDPOINT = ""  ##add your sheety(sheety.co) endpoint


class DataManager:
    def __init__(self):
        self.destination_data_sheet = {}

    def get_data(self):
        r = requests.get(url=SHEET_ENDPOINT)
        r.raise_for_status()
        self.data = r.json()
        print(self.data["prices"])
        for entry in self.data["prices"]:
            city_name = entry["city"]
            self.destination_data_sheet[city_name] = entry
        return self.data["prices"]

    def update_destination_code(self):
        fligh_search = FlightSearch()
        for city in self.destination_data_sheet:
            if "iataCode" not in city:
                self.data = {
                    "price": {"iataCode": fligh_search.get_city_codes(city["city"])}
                }
                response = requests.put(
                    url=f"{SHEET_ENDPOINT}/{city['id']}", json=self.data
                )
                print(response.text)

    def add_destination(self, user_city):
        new_city_params = {"price": {"city": user_city}}
        r = requests.post(SHEET_ENDPOINT, json=new_city_params)
        data = r.json()
        print(self.destination_data_sheet)
        print(f"\nTHIS IS THE NEW DATA{data['price']}", self.destination_data_sheet)
        self.destination_data_sheet.append(data["price"])
        self.get_data()
        self.update_destination_code()

    def delete_destination(self, user_city):
        self.id = 0
        for city in self.destination_data_sheet:
            if city["city"] == user_city:
                self.id = city["id"]
                self.destination_data_sheet.remove(city)

        r = requests.delete(f"{SHEET_ENDPOINT}/{self.id}")
        print(r.text)

    # found some white spaces in the names, here's a quick fix
    def fix_names(self):
        for city in self.destination_data_sheet:
            if " " in city["city"]:
                self.edit_data = {"price": {"city": city["city"].rstrip()}}
                r = requests.put(f"{SHEET_ENDPOINT}/{city['id']}", json=self.edit_data)

    # prints the current state of the sheet
    def print_sheet(self):
        self.get_data()
        print(self.destination_data_sheet)

    # the main function in the code
    def update_latest_prices(self, data):
        # gets the latest
        for n in range(len(data["data"])):
            city_to_check = unidecode(data["data"][n]["cityTo"])
            if (
                city_to_check in self.destination_data_sheet
                and data["data"][n]["price"]
                < self.destination_data_sheet[city_to_check]["lowestPrice"]
            ):
                update_params = {
                    "price": {
                        "lowestPrice": data["data"][n]["price"],
                        "currentPrice": data["data"][n]["price"],
                    },
                }
                r = requests.put(
                    url=f"{SHEET_ENDPOINT}/{self.destination_data_sheet[city_to_check]['id']}",
                    json=update_params,
                )
                r.raise_for_status()
            elif (
                city_to_check in self.destination_data_sheet
                and data["data"][n]["price"]
                >= self.destination_data_sheet[city_to_check]["lowestPrice"]
            ):
                update_params = {"price": {"currentPrice": data["data"][n]["price"]}}
                r = requests.put(
                    url=f"{SHEET_ENDPOINT}/{self.destination_data_sheet[city_to_check]['id']}",
                    json=update_params,
                )
                r.raise_for_status()
