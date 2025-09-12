import requests
import json
from requests.auth import HTTPBasicAuth
import os
from dotenv import load_dotenv

load_dotenv()

SMS_USERNAME = os.getenv("SMS_USERNAME")
SMS_PASSWORD = os.getenv("SMS_PASSWORD")
SMS_API_SOURCE = os.getenv("SMS_API_SOURCE", "DefaultSource")
SMS_API_URL = "https://api.smsleopard.com/v1/sms/send"

def create_alert_message(trap_id, fill_level):
    template = (
        "Alert from FruitGuard:\n\n"
        "Trap {trap_id} fill level is {fill_level}.\n\n"
        "Please empty the trap soon to avoid fruit fly infestation.\n\n"
        "Thank you!"
    )
    return template.format(trap_id=trap_id, fill_level=fill_level)
def send_sms(phone_number, message):
    body = {
        "message": message,
        "source": SMS_API_SOURCE,  
        "destination": [
            {
                "number": phone_number,
            },
        ]
    }
    try:
        response = requests.post(
            SMS_API_URL,
            data=json.dumps(body),
            auth=HTTPBasicAuth(SMS_USERNAME, SMS_PASSWORD),
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        response.raise_for_status()
        print("SMS sent successfully:", response.json())
    except requests.RequestException as e:
        print(f"Failed to send SMS: {e}")
if __name__ == "__main__":
   
    test_phone = "254713200280"  
    test_message = create_alert_message("TRAP123", 7)
    send_sms(test_phone, test_message)