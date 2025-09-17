from django.shortcuts import render
from rest_framework import viewsets
from .serializers import DataMonitoringSerializer
from data_monitoring.models import DataMonitoring
from device.models import Device
from .serializers import DeviceSerializer
from django.contrib.auth import get_user_model, authenticate
from rest_framework import generics, status, viewsets, permissions
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from .serializers import UserSerializer, LoginSerializer


# Create your views here.
class DataMonitoringViewSet(viewsets.ModelViewSet):
   queryset = DataMonitoring.objects.all()
   serializer_class = DataMonitoringSerializer

   def create(self, request, *args, **kwargs):
       api_payload = request.data
       serializer = self.get_serializer(data=api_payload)

       try:
           if serializer.is_valid():
               serializer.save()
               if hasattr(request, 'msg') and request.msg.topic == "esp32/alert" and api_payload["trap_fill_level"] > 0:
                   from api.sms import send_alert
                   device_pk = api_payload.get('device_pk')
                   send_alert(device_pk, api_payload['trap_fill_level'])
               response = requests.post(API_URL.rstrip('/') + '/data_monitoring/', json=api_payload)

               return Response(serializer.data, status=201)
           else:
               return Response(serializer.errors, status=400)
       except json.JSONDecodeError:
           pass  
       except Exception as e:
           pass   

class DeviceViewSet(viewsets.ModelViewSet):
    queryset = Device.objects.all()
    serializer_class = DeviceSerializer

User = get_user_model()

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.AllowAny]

class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [AllowAny]

class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        token, _ = Token.objects.get_or_create(user=user)
        return Response({
            "token": token.key,
            "user_id": str(user.id),
            "user_type": user.user_type,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "email": user.email,
        }, status=status.HTTP_200_OK)

      

class ProfileView(generics.RetrieveAPIView):
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user
