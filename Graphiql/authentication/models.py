from django.db import models

# Create your models here.
from django.db import models
from django.contrib.auth.models import AbstractUser, UserManager
from django.utils.translation import gettext_lazy as _
from django_countries.fields import CountryField
from .validators import password_regex_pattern
import uuid
from .validators import minimum_amount
from phonenumber_field.modelfields import PhoneNumberField


class CustomUserManager(UserManager):
    use_in_migrations = True
    """
    Custom user model manager where email is the unique identifiers
    for authentication instead of usernames.
    """

    def _create_user(self, email, password, **extra_fields):
        """
        Creates and saves a User with the given email and password.
        """
        if not email:
            raise ValueError("The given email must be set")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_superuser", False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password):
        """
        Create and save a SuperUser with the given email and password.
        """
        user = self._create_user(email=email, password=password)
        user.is_admin = True
        user.is_staff = True
        user.is_superuser = True
        user.is_active = True
        user.is_verified = True
        user.save(using=self.db)
        return user


class User(AbstractUser):
    username = None
    USER_TYPE = [("Tenant", "Tenant"), ("Agent", "Agent")]
    entry = models.CharField(choices=USER_TYPE, max_length=10)
    email = models.EmailField(_("email address"), unique=True)
    user_id = models.UUIDField(
        default=uuid.uuid4, editable=False, primary_key=True, unique=True
    )
    name = models.CharField(
        max_length=20, blank=True, null=True, verbose_name="Full Name"
    )
    profile_image = models.ImageField(
        upload_to="profile/", blank=True, null=True
    )
    background_image = models.ImageField(
        upload_to="profile/", blank=True, null=True
    )
    country = CountryField()
    phone_number = PhoneNumberField(null=True, blank=True, unique=True)
    password = models.CharField(max_length=20, validators=[password_regex_pattern])
    date_created = models.DateTimeField(auto_now_add=True)
    is_user = models.BooleanField(default=True)
    is_verify = models.BooleanField(default=False)
  

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []
    objects = CustomUserManager()

    def __str__(self):
        return self.email



class Agent(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    agent_location = models.CharField(max_length=150, null=True, blank=True)
    balance = models.FloatField(
        default=0,
        validators=[
            minimum_amount,
        ],
    )
