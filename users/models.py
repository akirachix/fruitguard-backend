

from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models

USER_TYPE_CHOICES = [
    ('farmer', 'Farmer'),
    ('agrovet', 'Agrovet'),
    ('admin', 'Admin'),
]

class UserManager(BaseUserManager):
    use_in_migrations = True

    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        if password: 
            user.set_password(password)
        else:  
            user.set_unusable_password()
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)
        extra_fields.setdefault('user_type', 'admin')
        
        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')
        if not password:
            raise ValueError('Superuser must have a password.')

        return self.create_user(email, password, **extra_fields)

class User(AbstractUser):
    username = None  
    first_name = models.CharField(max_length=50, blank=True)
    last_name = models.CharField(max_length=50, blank=True)
    phone_number = models.CharField(max_length=50,unique=True)
    number_of_traps=models.CharField(blank=True,null=True)
    email = models.EmailField('email address', blank=True, null=True, unique=True)
    location = models.CharField(max_length = 50, blank = True, null=True)
    number_of_traps = models.IntegerField(blank = True, null=True)
    profile_image = models.ImageField(upload_to='profile_images/', blank=True, null=True)
    user_type = models.CharField(max_length=50, choices=USER_TYPE_CHOICES, default='farmer')
    location=models.CharField(blank=True,null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name', 'user_type']

    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.user_type})"
