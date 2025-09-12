from django.db import models
from users.models import User

# Create your models here.

class Device(models.Model):
    DEVICE_STATUS=[
        ('active', 'Active'),
        ('inactive', 'Inactive'),
]

    device_id = models.BigAutoField(primary_key=True)
    device_identifier = models.CharField(max_length=100, unique=True, null=True, blank=True)
    status= models.CharField(max_length=50, choices= DEVICE_STATUS, default='Active')
    user_id=models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    created_at = models.DateField(auto_now_add=True)

    def __str__(self):
        return f"Device{self.device_id} ({self.status})"



