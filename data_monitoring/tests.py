
from django.test import TestCase
from django.utils import timezone
from .models import DataMonitoring

# Create your tests here.

class DataMonitoringModelTest(TestCase):

    def setUp(self):
        self.data_monitoring = DataMonitoring.objects.create(level_reading=100)

    def test_created_at_auto_now_add(self):
        self.assertIsNotNone(self.data_monitoring.created_at)
        self.assertLessEqual(self.data_monitoring.created_at, timezone.now())

    def test_level_reading_field(self):
        self.assertEqual(self.data_monitoring.level_reading, 100)

    def test_string_representation(self):
        self.assertEqual(str(self.data_monitoring), "100")

    def test_default_values(self):
        data_monitoring = DataMonitoring.objects.create(level_reading=50)
        self.assertIsNotNone(data_monitoring.created_at)
        self.assertEqual(data_monitoring.level_reading, 50)

    def test_device_id_field(self):
        data_monitoring = DataMonitoring.objects.create(level_reading=75, device_id=1)
        self.assertEqual(data_monitoring.device_id.id, 1)
    
 