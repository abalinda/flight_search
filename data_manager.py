import requests
import json
from unidecode import unidecode
from datetime import datetime as dt
from flight_search import FlightSearch
from notification_manager import NotificationManager
from datetime import datetime

SHEET_ENDPOINT = #enter your sheety endpoint


class DataManager:
    def __init__(self):
        self.destination_data_sheet = {}
        self.notification_manager = NotificationManager()

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
                print(
                    f"GOT A LOWER PRICE FOR{city_to_check} at {data['data'][n]['price']}"
                )
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
                # send SMS
                self.notification_manager.send_sms(
                    price=data["data"][n]["price"],
                    city_from_name=city_to_check,
                    city_from_iata=data["data"][n]["cityCodeFrom"],
                    city_to_name=data["data"][n]["cityTo"],
                    city_to_iata=data["data"][n]["cityCodeTo"],
                    departure_date=datetime.strptime(
                        data["data"][n]["local_departure"], "%Y-%m-%dT%H:%M:%S.%fZ"
                    ).strftime("%d-%m-%Y at %H:%M local time"),
                    return_date=datetime.strptime(
                        data["data"][n]["route"][1]["local_departure"],
                        "%Y-%m-%dT%H:%M:%S.%fZ",
                    ).strftime("%d-%m-%Y at %H:%M local time"),
                    kiwi_url=data["data"][n]["deep_link"],
                )
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
