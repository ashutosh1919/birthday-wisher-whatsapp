from datetime import datetime
import os

from apscheduler.schedulers.background import BackgroundScheduler
from flask import Flask
import pandas as pd
from twilio.rest import Client

app = Flask(__name__)

account_sid = os.environ.get('ACCOUNT_SID')
auth_token = os.environ.get('AUTH_TOKEN')
client = Client(account_sid, auth_token)


def send_birthday_wish(client, recipient_number, recipient_name):
    """Send a birthday wish to a recipient using their WhatsApp number.

    Args:
        client (object): An instantiation of the Twilio API's Client object
        recipient_number (str): The number associated with the recipient's WhatsApp account,
            including the country code, and prepended with '+'. For example, '+14155238886'.
        recipient_name (str): The recipient's name

    Returns:
        True if successful, otherwise returns False
    """

    birthday_wish = """
        Hey {}, this is Ashutosh's personal birthday wisher.
        Happy Birthday to you! I wish you all the happiness that you deserve.
        I am so proud of you.""".format(recipient_name)

    try:
        message = client.messages.create(
            body=birthday_wish,
     	    from_='whatsapp:+14155238886',  # The default Sandbox number provided by Twilio
     	    to='whatsapp:' + recipient_number
        )

        print("Birthday wish sent to", recipient_name, "on WhatsApp number", recipient_number)
        return True

    except Exception as e:
        print("Something went wrong. Birthday message not sent.")
        print(repr(e))
        return False

def create_birthdays_dataframe():
    """Create a pandas dataframe containing birth date information from a CSV file.

    Args:
        None

    Returns:
        A dataframe if successful, otherwise returns False.
    """

    try:
        dateparse = lambda x: datetime.strptime(x, "%m-%d-%Y")
        birthdays_df = pd.read_csv(
            "birth_dates.csv",
            dtype=str,
            parse_dates=['Birth Date'],
            date_parser=dateparse
        )
        print(birthdays_df)
        return birthdays_df

    except Exception as e:
        print("Something went wrong. Birthdays dataframe not created.")
        print(repr(e))
        return False

def check_for_matching_dates():
    """Calls the send_birthday_wish() function if today is someone's birthday.

    Args:
        None
    Returns:
        True if successful, otherwise returns False.
    """
    try:
        birthdays_df = create_birthdays_dataframe()
        birthdays_df["day"] = birthdays_df["Birth Date"].dt.day
        birthdays_df["month"] = birthdays_df["Birth Date"].dt.month
        today = datetime.now()
        for i in range(birthdays_df.shape[0]):
            birthday_day = birthdays_df.loc[i, "day"]
            birthday_month = birthdays_df.loc[i, "month"]
            if today.day == birthday_day and today.month == birthday_month:
                send_birthday_wish(client, birthdays_df.loc[i, "WhatsApp Number"], birthdays_df.loc[i, "Name"])
        return True

    except Exception as e:
        print("Something went wrong. Birthday check not successful.")
        print(repr(e))
        return False

scheduler = BackgroundScheduler()
job = scheduler.add_job(check_for_matching_dates, 'cron', day_of_week ='mon-sun', hour=0, minute=1)
scheduler.start()

if __name__ == '__main__':
    app.run()