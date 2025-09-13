
from rest_framework import serializers
from data_monitoring.models import DataMonitoring 
from device.models import Device
from django.contrib.auth import get_user_model, authenticate
from rest_framework.validators import UniqueValidator

class DataMonitoringSerializer(serializers.ModelSerializer):
   class Meta:
       model = DataMonitoring
       fields = '__all__' 

class DeviceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Device
        fields = '__all__'





User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=False)  
    email = serializers.EmailField(
        required=False,
        allow_blank=True,
        validators=[
            UniqueValidator(queryset=User.objects.all(), message="This email is already in use.")
        ]
    )
    profile_image = serializers.ImageField(required=False, allow_null=True)

    class Meta:
        model = User
        fields = [
            "id",
            "first_name",
            "last_name",
            "phone_number",
            "email",
            "location",
            "number_of_traps",
            "profile_image",
            "user_type",
            "password",
            "created_at",
        ]
        read_only_fields = ["id", "created_at"]

    def validate_phone_number(self, value):
        print(f"phone number !!{value} @@@")
        if not value.isdigit():
            raise serializers.ValidationError("Phone number must contain digits only.")
        if len(value) < 10 or len(value) > 15:
            raise serializers.ValidationError("Phone number must be between 10 and 15 digits.")
        return value

    def create(self, validated_data):
        password = validated_data.pop('password', None)
        user_type = validated_data.get('user_type')

        if validated_data.get("email") == "":
            validated_data["email"] = None

        user = User(**validated_data)

        if user_type in ['agrovet', 'admin']:
            if not password:
                raise serializers.ValidationError("Password is required for agrovet and admin users.")
            user.set_password(password)
        else:
            user.set_unusable_password()

        user.save()
        return user

class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        email = data.get("email")
        password = data.get("password")

        if not email or not password:
            raise serializers.ValidationError("Must include 'email' and 'password'.")

        user = authenticate(username=email, password=password)
        if not user:
            raise serializers.ValidationError("Invalid email or password.")

        if user.user_type not in ["agrovet", "admin"]:
            raise serializers.ValidationError("User type not allowed to login.")

        data['user'] = user
        return data
