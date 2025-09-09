from rest_framework import serializers
from data_monitoring.models import DataMonitoring 


class DataMonitoringSerializer(serializers.ModelSerializer):
   class Meta:
       model = DataMonitoring
       fields = '__all__' 
