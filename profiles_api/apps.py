"""App configuration for the profiles API app."""
from django.apps import AppConfig


class ProfilesApiConfig(AppConfig):
    """Django AppConfig for the profiles_api application."""
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'profiles_api'
