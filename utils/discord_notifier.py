import requests
from dotenv import load_dotenv
import os

load_dotenv()


def send_discord_alert(message):
    webhook_url = os.getenv('spotify_bot_webhook')

    data = {
        "content": f"Spotify Tracker Failed:\n{message}"
    }
    response = requests.post(webhook_url, json=data)

    if response.status_code == 204:
        print("Alert sent successfully to Discord.")
    else:
        print(f"Failed to send alert to Discord: {response.status_code}")
