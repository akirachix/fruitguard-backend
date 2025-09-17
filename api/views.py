from django.shortcuts import render
from rest_framework import viewsets
from .serializers import DataMonitoringSerializer
from data_monitoring.models import DataMonitoring
from device.models import Device
from .serializers import DeviceSerializer
from django.contrib.auth import get_user_model, authenticate
from rest_framework import generics, status, viewsets, permissions
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny,IsAuthenticated
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from .serializers import UserSerializer, LoginSerializer
from rest_framework.decorators import api_view
from rest_framework.parsers import MultiPartParser, FormParser

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

@api_view(['GET'])
def device_html_view(request):
    devices = Device.objects.all()  
    serializer = DeviceSerializer(devices, many=True)
    return render(request, 'device.html', {'devices': serializer.data})

User = get_user_model()

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        queryset = User.objects.all()
        user_type = self.request.query_params.get('user_type')
        if user_type:
            queryset = queryset.filter(user_type=user_type)
        return queryset


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

      

class ProfileView(generics.RetrieveUpdateAPIView):
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser] 

    def get_object(self):
        return self.request.user
    
    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', True)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(serializer.data, status=status.HTTP_200_OK)

