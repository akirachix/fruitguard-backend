
from django.test import TestCase
from django.utils import timezone
from .models import DataMonitoring
from device.models import Device


# Create your tests here.

class DataMonitoringModelTest(TestCase):
     def setUp(self):
        self.device = Device.objects.create(device_id="786")
        self.data_monitoring = DataMonitoring.objects.create(trap_fill_level=100, device=self.device)

     def test_created_at_auto_now_add(self):
        self.assertIsNotNone(self.data_monitoring.created_at)
        self.assertLessEqual(self.data_monitoring.created_at, timezone.now())

     def test_trap_fill_level_field(self):
        self.assertEqual(self.data_monitoring.trap_fill_level, 100)

     def test_string_representation(self):
        self.assertEqual(str(self.data_monitoring), "100")

     def test_default_values(self):
        device = Device.objects.create(device_id="1234")
        data_monitoring = DataMonitoring.objects.create(trap_fill_level=50, device=device)
        self.assertIsNotNone(data_monitoring.created_at)
        self.assertEqual(data_monitoring.trap_fill_level, 50)

     def test_device_id_field(self):
        device = Device.objects.create() 
        data_monitoring = DataMonitoring.objects.create(trap_fill_level=75, device=device)
        self.assertEqual(data_monitoring.device.device_id, device.device_id) 
