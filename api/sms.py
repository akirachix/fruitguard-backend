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


load_dotenv()
SMS_USERNAME = os.getenv("SMS_USERNAME")
SMS_PASSWORD = os.getenv("SMS_PASSWORD")
SMS_API_SOURCE = os.getenv("SMS_API_SOURCE")
SMS_API_URL = "https://api.smsleopard.com/v1/sms/send"

def create_alert_message(first_name, trap_id, fill_level):
      
    if fill_level == 5:
        template = (
        "Hello {first_name},\n"
        "Your trap is almost full.\n"
        "Please empty it as soon as possible to keep fruit flies under control.\n"
        "Thank you!"
    )
    elif fill_level == 4:
        template = (
        "Hello {first_name},\n"
        "Warning: Your trap is full.\n"
        "Please empty it now to prevent fruit flies from overflowing and damaging your mangoes.\n"
        "Thank you!"
    )
    return template.format(first_name=first_name, trap_id=trap_id, fill_level=fill_level)

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

def send_alert(device_pk, fill_level):
    from device.models import Device
    threshold = getattr(settings, 'TRAP_FILL_THRESHOLD', 5)
    if fill_level <= threshold:
        try:
            device = Device.objects.select_related('user_id').get(device_id=device_pk)
            phone_number = device.user_id.phone_number if device.user_id else None
            if phone_number:
                phone_number = phone_number.strip()
                if phone_number.startswith("+"):
                    phone_number = phone_number[1:]
                if not phone_number.startswith("254") and phone_number.startswith("0"):
                    phone_number = "254" + phone_number[1:]
                farmer_name = getattr(device.user_id, 'first_name', None) or "Farmer"
                message = create_alert_message(farmer_name, device.device_identifier, fill_level)
                send_sms(phone_number, message)
            else:
                print(f"No phone number linked to device {device_pk}.")
        except Device.DoesNotExist:
            print(f"Device {device_pk} not found in database.")
    else:
        print(f"Trap fill level {fill_level} threshold {threshold}, no alert sent.")
        
if __name__ == "__main__":
    import django
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'fruitguard.settings')
    django.setup()
    test_device_id = 10
    test_fill_level = 5
    send_alert(test_device_id, test_fill_level)