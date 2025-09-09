
from django.shortcuts import render
from rest_framework import viewsets
from django.http import Http404
from .serializers import DataMonitoringSerializer
from data_monitoring.models import DataMonitoring

# Create your views here.
class DataMonitoringViewSet(viewsets.ModelViewSet):
    queryset = DataMonitoring.objects.all()
    serializer_class = DataMonitoringSerializer

    def get_object(self):
        pk = self.kwargs.get('pk')
        try:
            return DataMonitoring.objects.get(pk=pk)
        except DataMonitoring.DoesNotExist:
            raise Http404

