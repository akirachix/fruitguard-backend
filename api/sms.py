import sys
import os
import json
import requests
from requests.auth import HTTPBasicAuth
from dotenv import load_dotenv
from django.conf import settings
import django

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'fruitguard.settings')
django.setup()

from device.models import Device
from data_monitoring.mqtt import check_alert
load_dotenv()
SMS_USERNAME = os.getenv("SMS_USERNAME")
SMS_PASSWORD = os.getenv("SMS_PASSWORD")
SMS_API_SOURCE = os.getenv("SMS_API_SOURCE", "DefaultSource")
SMS_API_URL = "https://api.smsleopard.com/v1/sms/send"

def create_alert_message(trap_id, fill_level):
    template = (
        "Hello, this is FruitGuard. \n\n"
        "Trap {trap_id} fill level is {fill_level}.\n\n"
        "Please empty the trap soon to avoid fruit fly infestation.\n\n"
        "Thank you!"
    )
    return template.format(trap_id=trap_id, fill_level=fill_level)

def send_sms(phone_number, message):
    body = {
        "message": message,
        "source": SMS_API_SOURCE,
        "destination": [{"number": phone_number}],
    }
    try:
        response = requests.post(
            SMS_API_URL,
            data=json.dumps(body),
            auth=HTTPBasicAuth(SMS_USERNAME, SMS_PASSWORD),
            headers={"Content-Type": "application/json"},
            timeout=10,
        )
        response.raise_for_status()
        print(f"SMS sent successfully to {phone_number}: {response.json()}")
    except requests.RequestException as e:
        print(f"Failed to send SMS to {phone_number}: {e}")

def send_alert(device_id, fill_level):
    check_alert(device_id, fill_level)
    
if __name__ == "__main__":
    test_device_id = 10
    test_fill_level = 8
    send_alert(test_device_id, test_fill_level)