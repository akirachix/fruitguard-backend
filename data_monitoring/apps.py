import threading
import paho.mqtt.client as mqtt
from django.apps import AppConfig
from django.conf import settings
import ssl
import time

def mqtt_thread():
    client = mqtt.Client(client_id="backendClient")

    def on_connect(client, userdata, flags, rc):
        if rc == 0:
            client.subscribe("esp32/alert")

    def on_message(client, userdata, msg):
        pass

    client.on_connect = on_connect
    client.on_message = on_message
    client.username_pw_set(settings.MQTT_USER, settings.MQTT_PASSWORD)
    
    try:
        client.tls_set()
        client.tls_insecure_set(False) 
    except ssl.SSLError:
        pass

    while True:
        try:
            client.connect(settings.MQTT_SERVER, settings.MQTT_PORT, 60)
            client.loop_forever()
        except ssl.SSLError as e:
            time.sleep(5)
        except Exception as e:
            time.sleep(5)
            continue

class DataMonitoringConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'data_monitoring'
    _mqtt_thread_started = False

    def ready(self):
        if not DataMonitoringConfig._mqtt_thread_started:
            DataMonitoringConfig._mqtt_thread_started = True
            thread = threading.Thread(target=mqtt_thread)
            thread.daemon = True
            thread.start()
