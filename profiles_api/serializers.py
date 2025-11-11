from rest_framework import serializers
from .models import User


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "email", "name", "password", "role"]
        extra_kwargs = {"password": {"write_only": True}}

    def validate_email(self, value):
        """Check if email is unique and valid format."""
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("This email is already registered.")
        if "@" not in value or "." not in value:
            raise serializers.ValidationError("Enter a valid email address.")
        return value

   
    def validate_name(self, value):
        """Ensure name is not empty and has at least 3 characters."""
        if not value.strip():
            raise serializers.ValidationError("Name cannot be empty.")
        if len(value.strip()) < 3:
            raise serializers.ValidationError("Name must be at least 3 characters long.")
        return value

  
    def validate_password(self, value):
        """Password must be exactly 7 characters."""
        if len(value) != 7:
            raise serializers.ValidationError("Password must be exactly 7 characters long.")
        return value
    
    def create(self, validated_data):
        password = validated_data.pop("password", None)
        user = User(**validated_data)
        if password:
            user.set_password(password)
        user.save()
        return user
