import json
import requests
import paho.mqtt.client as mqtt
from django.conf import settings
from device.models import Device
from api.serializers import DataMonitoringSerializer
device_map = {}
def fetch_device_map():
    global device_map
    try:
        response = requests.get(settings.MQTT_API_URL.replace('/data_monitoring/', '/device/'))
        response.raise_for_status()
        devices = response.json()
        device_map = {d['device_identifier']: d['device_id'] for d in devices}
    except Exception as e:
        print(f"Failed to fetch device map: {e}")
def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("Connected to MQTT broker")
        client.subscribe(settings.MQTT_TOPIC)
    else:
        print(f"Failed to connect, return code {rc}")

def on_message(client, userdata, msg):
    try:

        payload = json.loads(msg.payload.decode())
        device_key = str(payload.get('device_id'))
        device_pk = device_map.get(device_key)
        if device_pk is None:
            try:
                device_pk = int(device_key)
            except ValueError:
                print(f"Device key {device_key} not found in device_map and not numeric.")
                return
        data = {
            'device': device_pk,
            'trap_fill_level': payload.get('distance', 0),
        }
        serializer = DataMonitoringSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            check_alert(device_pk, data['trap_fill_level'])
        else:
            print(f"Serializer invalid: {serializer.errors}")
    except Exception as e:
        print(f"Error processing MQTT message: {e}")

def get_farmers_phone_number(device_pk):
    try:
        device = Device.objects.select_related('user_id').get(device_id=device_pk)
        return device.user_id.phone_number if device.user_id else None
    except Device.DoesNotExist:
        print(f"Device {device_pk} not found in database.")
        return None

def get_fill_threshold():
    return getattr(settings, 'TRAP_FILL_THRESHOLD', 7)

def check_alert(device_pk, fill_level):
    from api.sms import send_sms
    threshold = get_fill_threshold()
    if fill_level >= threshold:
        phone_number = get_farmers_phone_number(device_pk)
        if phone_number:
            message = f"Alert! Trap fill level {fill_level} exceeded threshold {threshold}."
            send_sms(phone_number, message)
        else:
            print(f"No phone number linked to device {device_pk} user.")
    else:
        print(f"Trap fill level {fill_level} below threshold {threshold}, no alert sent.")

def mqtt_thread():
    fetch_device_map()
    client = mqtt.Client(client_id="backendClient")
    client.username_pw_set(settings.MQTT_USERNAME, settings.MQTT_PASSWORD)
    client.tls_set()
    client.on_connect = on_connect
    client.on_message = on_message
    client.connect(settings.MQTT_BROKER, settings.MQTT_PORT, 60)
    client.loop_forever()