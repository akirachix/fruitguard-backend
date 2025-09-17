import json
import os
import threading
import time
import requests
import paho.mqtt.client as mqtt
import ssl
from dotenv import load_dotenv
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from django.conf import settings


load_dotenv(override=True)
BROKER = os.getenv('BROKER')
PORT = int(os.getenv('PORT'))
USERNAME = os.getenv('USERNAME')
PASSWORD = os.getenv('PASSWORD')
TOPIC = os.getenv('TOPIC', 'esp32/#')
API_URL = os.getenv('API_URL')


device_map = {}


def fetch_device_map():
    global device_map
    if not API_URL:
        return
    session = requests.Session()
    retries = Retry(total=5, backoff_factor=2, status_forcelist=[502, 503, 504, 111])
    session.mount('http://', HTTPAdapter(max_retries=retries))
    try:
        devices_url = API_URL.rstrip('/') + '/device/'
        response = session.get(devices_url, timeout=10)
        response.raise_for_status()
        devices = response.json()
        if not isinstance(devices, list):
            return
        device_map.clear()
        device_map.update({str(d['device_identifier']).strip().lower(): d['device_id'] for d in devices})
    except requests.exceptions.RequestException:
        pass
    except ValueError:
        pass
    except KeyError:
        pass


def on_connect(client, userdata, flags, rc, properties=None):
    if rc == 0:
        topics = [
            ("esp32/alert", 1)
        ]
        client.subscribe(topics)


def on_message(client, userdata, msg):
    from api.serializers import DataMonitoringSerializer
    try:
        payload_str = msg.payload.decode("utf-8", errors="ignore").strip()
        payload = json.loads(payload_str)
        device_key = str(payload.get('device_id')).strip().lower()
        device_pk = device_map.get(device_key)
        if device_pk is None:
            return
        api_payload = {
            "device": device_pk,
            "topic": msg.topic,
            "trap_fill_level": payload.get('distance', 0) if msg.topic == "esp32/alert" else 0,
            "metadata": payload
        }
        serializer = DataMonitoringSerializer(data=api_payload)
        if serializer.is_valid():
            serializer.save()
            if msg.topic == "esp32/alert" and api_payload["trap_fill_level"] > 0:
                from api.sms import send_alert
                send_alert(device_pk, api_payload['trap_fill_level'])
        response = requests.post(API_URL.rstrip('/') + '/data_monitoring/', json=api_payload)
    except json.JSONDecodeError:
        pass
    except Exception:
        pass


class MqttThread(threading.Thread):
    def run(self):
        time.sleep(15) 
        fetch_device_map()
        client = mqtt.Client(client_id="backendClient")
        client.on_connect = on_connect
        client.on_message = on_message
        client.username_pw_set(USERNAME, PASSWORD)
        cert_path = os.path.join(os.path.dirname(__file__), 'isrgrootx1.pem')
        client.tls_set(ca_certs=cert_path, tls_version=ssl.PROTOCOL_TLS_CLIENT)
        client.tls_insecure_set(False)
        try:
            client.connect(BROKER, PORT, keepalive=60)
            client.loop_forever()
        except Exception:
            pass
