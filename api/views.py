

from django.shortcuts import render
from rest_framework import viewsets
from django.shortcuts import get_object_or_404
from .serializers import DataMonitoringSerializer
from data_monitoring.models import DataMonitoring


# Create your views here.
class DataMonitoringViewSet(viewsets.ModelViewSet):
   queryset = DataMonitoring.objects.all()
   serializer_class = DataMonitoringSerializer


   def get_object(self):
       pk = self.kwargs.get('pk')
       return get_object_or_404(DataMonitoring, pk=pk)
