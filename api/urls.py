
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import DataMonitoringViewSet, RegisterView, LoginView, ProfileView
from .views import DeviceViewSet,UserViewSet

router = DefaultRouter()
router.register(r"data_monitoring", DataMonitoringViewSet, basename="data_monitoring")
router.register(r'device', DeviceViewSet)
router.register(r'users', UserViewSet, basename='user')

urlpatterns = [
   path("", include(router.urls)),
   path('api/', include(router.urls)),
   path("register/", RegisterView.as_view(), name="register"),
   path("login/", LoginView.as_view(), name="login"),
   path("profile/", ProfileView.as_view(), name="profile"),


   
]




