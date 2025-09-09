from django.db import models
from device.models import Device


# Create your models here.
class DataMonitoring(models.Model):
   device = models.ForeignKey(Device, on_delete=models.CASCADE)
   trap_fill_level = models.IntegerField()
   updated_at = models.DateTimeField(auto_now=True)
   created_at = models.DateTimeField(auto_now_add=True)
  
   def __str__(self):
       return f"{self.trap_fill_level}"
   