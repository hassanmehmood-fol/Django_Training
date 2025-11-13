"""Custom user model and manager for the profiles API app."""

from django.db import models
from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    PermissionsMixin,
)

from django.conf import settings


class UserManager(BaseUserManager):
    """Manager providing helpers to create regular users and superusers."""

    def create_user(self, email, name, password=None, **extra_fields):
        """Create and return a new user with the given credentials and fields."""
        if not email:
            raise ValueError("Email field is required")
        if not extra_fields.get("role"):
            raise ValueError("Role field is required")

        email = self.normalize_email(email)
        user = self.model(email=email, name=name, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, name, password=None, **extra_fields):
        """Create and return a new superuser with elevated permissions."""
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("role", "teacher")

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True")

        return self.create_user(email, name, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    """Application user model using email as the username field."""

    ROLE_CHOICES = [
        ("student", "Student"),
        ("teacher", "Teacher"),
    ]

    email = models.EmailField(max_length=255, unique=True)
    name = models.CharField(max_length=255)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    objects = UserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["name", "role"]

    class Meta:
        db_table = "user"

    def __str__(self):
        return f"{self.email} ({self.role})"
    
    
    
class Feed(models.Model):
    """Model representing posts created by teachers."""

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="feeds"
    )
    text = models.TextField(max_length=1000, blank=True, null=True)
    image = models.ImageField(upload_to="feeds/", blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    likes = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name="liked_feeds",
        blank=True
    )

    class Meta:
        db_table = "feed"
        ordering = ["-created_at"]

    def __str__(self):
        return f"Feed by {self.user.email} - {self.text[:30]}"    
