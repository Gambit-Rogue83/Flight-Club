from data_manager import DataManager
from flight_search import FlightSearch
import time
from flight_data import FlightData as fd
from datetime import datetime, timedelta
from notification_manager import NotificationManager

########## SET UP FLIGHT SEARCH ###############

data_manager = DataManager()
sheet_data = data_manager.get_destination_data()
flight_search = FlightSearch()
notification_manager = NotificationManager()

#### ORIGIN AIRPORT ####
ORIGIN_CITY_IATA = "SLC"

######## UPDATE AIRPORT CODES ##############

for row in sheet_data:
    if row["iataCode"] == "":
        row["iataCode"] = flight_search.get_destination_code(row["city"])
        time.sleep(2)

print(f"sheet_data:\n {sheet_data}")

data_manager.destination_data = sheet_data
data_manager.update_destination_codes()


#### SEARCH FOR FLIGHTS #####

tomorrow = datetime.now() + timedelta(days=1)
seven_months_from_today = datetime.now() + timedelta(days=7 * 30)

for destination in sheet_data:
    print(f"Getting flights for {destination['city']}...")
    flights = flight_search.check_flights(
        ORIGIN_CITY_IATA,
        destination["iataCode"],
        from_time=tomorrow,
        to_time=seven_months_from_today
    )

    cheapest_flight = fd.find_cheapest_flight(flights)
    if cheapest_flight.price == "N/A":
        print(f"No direct flight to {destination['city']}. Looking for indirect flights...")
        stopover_flights = flight_search.check_flights(
            ORIGIN_CITY_IATA,
            destination["iataCode"],
            from_time=tomorrow,
            to_time=seven_months_from_today,
            is_direct=False
        )
        cheapest_flight = fd.find_cheapest_flight(stopover_flights)
        print(f"Cheapest indirect flight price is: ${cheapest_flight.price}")
        print(f"Lower price flight found to {destination['city']}!")
        notification_manager.send_sms(
            message_body=f"Low price alert! Only ${cheapest_flight.price} to fly"
            f"from {cheapest_flight.origin_airport} to {cheapest_flight.destination_airport},"
            f"on {cheapest_flight.out_date} until {cheapest_flight.return_date}."
        )







