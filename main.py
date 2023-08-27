from data_manager import DataManager
from flight_search import FlightSearch
from flight_data import FlightData
from pprint import pprint
import json
from datetime import datetime, timedelta


data_manager = DataManager()
flight_search = FlightSearch()
flight_data = FlightData()


# adds a new row in the sheet with the iata code retrived from the tequila api
def add_destination():
    add_city = input("What's the city you want to travel to?: ").title()
    data_manager.add_destination(add_city)


# delets a row from the sheet
def delete_destination():
    city_to_delete = input("What's the city you want to delete?: ").title()
    data_manager.delete_destination(city_to_delete)


# manually search for a flights, takes inputs: departure city, destination city, date range for departure, how many nights to stay
def manual_search():
    # gets user's outbound and destination as well as time frame for leaving and how many nights to stay
    from_where = input("What is your starting location(iata code): ").upper()
    where_to = input("Where would you like to go(iata code): ").upper()
    date1_from = input("When would you like to go (DD/MM/YYY) **from: ")
    date2_from = input("When would you like to go (DD/MM/YYY) **to: ")
    # gets the range of nights to stay from the user(if not correct input will asktry again)
    while True:
        how_many_nights = input(
            "How many nights would you like to stay?(range ex.:3-5): "
        )
        if "-" in how_many_nights:
            start_nights, end_nights = map(int, how_many_nights.split("-"))
            nights_range = [start_nights, end_nights]
            break
        else:
            print("Invalid input. Please provide a range in the format '3-5'. ")
    # checks the user's date intput if it matches the correct format and converts it into the matching str
    date_format = "%d/%m/%Y"
    try:
        date1_from = datetime.strptime(date1_from, date_format).strftime("%d/%m/%Y")
        date2_from = datetime.strptime(date2_from, date_format).strftime("%d/%m/%Y")
        date1_to = datetime.strptime(date1_to, date_format).strftime("%d/%m/%Y")
        date2_to = datetime.strptime(date2_to, date_format).strftime("%d/%m/%Y")

    except ValueError:
        print("Invalid date format please use dd/mm/yyyy")
    # calls the function to make manual search and passes the necessary data (check FlightSearch)
    flight_search.manual_search_flights(
        start=from_where,
        destination=where_to,
        date_from1=date1_from,
        date_from2=date2_from,
        start_nights=nights_range[0],
        end_nights=nights_range[1],
    )


# used for automatic search. calculates the today's date and 6 months from today
def get_from_dates():
    # find tomorrow as dd/mm/yyyy
    today = datetime.today()
    tomorrow = today + timedelta(days=1)
    date_from_1 = tomorrow.strftime("%d,%m,%Y-").strip("-").replace(",", "/")
    # find 6 months from today
    six_months_from_tdy = today + timedelta(days=6 * 30.44)
    date_from_2 = six_months_from_tdy.strftime("%d,%m,%Y-").strip("-").replace(",", "/")
    dates = [date_from_1, date_from_2]
    return dates


# checks the latest prices for return flights in the timerange of 6 months from today with 7-28 days of stay from SKP to all cities in the sheet and updates it
def automatic_search():
    destinations = []
    for city in data_manager.get_data():
        destinations.append(city["iataCode"])
    destinations_iata_codes = ", ".join(destinations).replace(" ", "")
    # timeframeot treba da e od denes+6 meseci za odenje e od 7 do 28 nokjevanja pred vrakjanje
    flights = flight_search.automatic_search_sheet(
        destinations_iata_codes, dates=get_from_dates()
    )
    data_manager.update_latest_prices(flights)
    return flights
