import os
from twilio.rest import Client


class NotificationManager:
    def __init__(self) -> None:
        self.twilio_auth_token = os.environ.get("TWILIO_AUT_TOKEN")
        self.twilio_account_sid = os.environ.get("TWILIO_ACCOUNT_SID")
        self.my_twilio_number = os.environ.get("my_twilio_number")
        self.my_br_number = os.environ.get("my_br_number")
        self.client = Client(self.twilio_account_sid, self.twilio_auth_token)

    def send_sms(self,price, city_from_name,city_from_iata, city_to_name,city_to_iata,departure_date,return_date, kiwi_url):
        message = self.client.messages.create(
                body=f"🤩 Low price alert! Only {price} to fly from {city_from_name}-{city_from_iata} to {city_to_name}-{city_to_iata} from {departure_date} to {return_date}. Book at {kiwi_url}:",
                from_=self.my_twilio_number,
                to=self.my_br_number,
            )
