import sys
import threading
import os
from django.apps import AppConfig

class DataMonitoringConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'data_monitoring'
   

class DataMonitoringConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "data_monitoring"
    _mqtt_thread_started = False
    _lock = threading.Lock()

    def ready(self):
        if any(cmd in sys.argv for cmd in ['makemigrations', 'migrate', 'check', 'collectstatic']):
            return
        if 'runserver' in sys.argv and not self._mqtt_thread_started and os.environ.get('RUN_MAIN') != 'true':
            with self._lock:
                if not self._mqtt_thread_started:
                    self._mqtt_thread_started = True
                    try:
                        from data_monitoring.mqtt import MqttThread
                        mqtt_thread = MqttThread()
                        mqtt_thread.daemon = True
                        mqtt_thread.start()
                    except ImportError as e:
                        raise
                    except Exception as e:
                        raise
