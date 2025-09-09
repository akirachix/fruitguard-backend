from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import DataMonitoringViewSet

router = DefaultRouter()
router.register(r"data_monitoring", DataMonitoringViewSet, basename="data_monitoring")

urlpatterns = [
    path("", include(router.urls)),
]