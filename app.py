from flask import Flask
from apscheduler.schedulers.background import BackgroundScheduler
import pandas as pd
from datetime import datetime
from twilio.rest import Client

app = Flask(__name__)

dateparse = lambda x: datetime.strptime(x, "%m-%d-%Y")
df_bday = pd.read_csv("birthdays.csv", dtype={0:str, 1:str, 2: str}, parse_dates=['Date'], date_parser=dateparse)

account_sid = 'AC97f4f8a453c151eb7d9ce72332b58f17'
auth_token = '0ecf334d0e8e3aed3eb9589c62ad5158'
client = Client(account_sid, auth_token)

def send_message(client, wapp_number, name):
    wish = "Hey {}, This is Ashutosh's personal birthday wisher. I wish you many many happy returns of the day and happy birthday to you. I wish all the happiness that you deserve. Keep working very hard and make everyone around you proud.".format(name)

    message = client.messages.create(
                                body=wish,
                                from_='whatsapp:+14155238886',
                                to='whatsapp:' + wapp_number
                            )

    # Log the information
    print("Birthday wish sent to", name, "on what's app number", wapp_number)

def scheduled_sender():
    df_bday["day"] = df_bday["Date"].dt.day
    df_bday["month"] = df_bday["Date"].dt.month
    today = datetime.now()
    for i in range(df_bday.shape[0]):
        d = df_bday.loc[i, "day"]
        m = df_bday.loc[i, "month"]
        if today.day == d and today.month == m:
            send_message(client, df_bday.loc[i, "Wapp Number"], df_bday.loc[i, "Name"])

scheduler = BackgroundScheduler()
job = scheduler.add_job(scheduled_sender, 'cron', day_of_week ='mon-sun', hour=0, minute=0)
scheduler.start()

if __name__ == '__main__':
    app.run()
