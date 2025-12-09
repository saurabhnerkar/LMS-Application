import uuid
import random
from datetime import timedelta
from django.utils import timezone
from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager


# -------------------------------
# Custom User Manager
# -------------------------------
class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("The Email field must be set")
        email = self.normalize_email(email)
        extra_fields.setdefault("is_active", True)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("role", "admin")

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")

        return self.create_user(email, password, **extra_fields)


# -------------------------------
# Custom User Model
# -------------------------------
class CustomUser(AbstractUser):
    ROLE_CHOICES = (
        ("student", "Student"),
        ("teacher", "Teacher"),
        ("admin", "Admin"),
    )

    username = models.CharField(max_length=150, unique=False, blank=True, null=True)
    email = models.EmailField(unique=True)
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default="student")
    profile_picture = models.ImageField(upload_to="profile_pictures/", blank=True, null=True)
    is_email_verified = models.BooleanField(default=False)
    email_verification_token = models.CharField(max_length=100, blank=True, null=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["role"]

    objects = CustomUserManager()

    def __str__(self):
        return f"{self.email} ({self.role})"

    def save(self, *args, **kwargs):
        if not self.username:
            self.username = self.email.split("@")[0]
        super().save(*args, **kwargs)

    # Optional helper methods
    def generate_verification_token(self):
        """Generate a unique verification token"""
        self.email_verification_token = str(uuid.uuid4())
        self.save(update_fields=["email_verification_token"])
        return self.email_verification_token

    def generate_login_otp(self):
        """Generate a 6-digit OTP for login verification"""
        from .models import LoginOTP  # ensure no circular import
        LoginOTP.objects.filter(user=self, is_used=False).update(is_used=True)
        otp = "".join([str(random.randint(0, 9)) for _ in range(6)])
        LoginOTP.objects.create(
            user=self,
            otp=otp,
            expires_at=timezone.now() + timedelta(minutes=10),
        )
        return otp


# -------------------------------
# OTP Model (if used)
# -------------------------------
class LoginOTP(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    otp = models.CharField(max_length=6)
    expires_at = models.DateTimeField()
    is_used = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"OTP for {self.user.email} - {self.otp}"

    def is_expired(self):
        """Return True if the OTP is past its expiry time."""
        return timezone.now() > self.expires_at