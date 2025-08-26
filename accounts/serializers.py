from rest_framework import serializers
from django.core.mail import send_mail
from django.contrib.auth import authenticate
from .models import CustomUser
from .models import UserProfile
from .utils import get_tokens_for_user
from django.contrib.auth import get_user_model
import random

User = get_user_model()

class SignupSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ["email", "username", "full_name", "phone_number", "password"]

    def create(self, validated_data):
        password = validated_data.pop("password")
        user = User(**validated_data)
        user.set_password(password)

        # Generate 6-digit verification code
        code = str(random.randint(100000, 999999))
        user.verification_code = code
        user.save()

        # Send verification email
        send_mail(
            subject="Verify Your Account",
            message=f"Your verification code is {code}",
            from_email=None,  # defaults to DEFAULT_FROM_EMAIL
            recipient_list=[user.email],
            fail_silently=False,
        )

        return user



class VerifyAccountSerializer(serializers.Serializer):
    email = serializers.EmailField()
    code = serializers.CharField(max_length=6)

    def validate(self, data):
        try:
            user = CustomUser.objects.get(email=data['email'])
        except CustomUser.DoesNotExist:
            raise serializers.ValidationError("User not found")

        if user.verification_code != data['code']:
            raise serializers.ValidationError("Invalid code")
        return data

class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)
    
    def validate(self, data):
        email = data.get('email')
        password = data.get('password')

        if email and password:
            user = authenticate(username=email, password=password)
            if user:
                if not user.is_verified:
                    raise serializers.ValidationError("Account not verified.")
                data['user'] = user
            else:
                raise serializers.ValidationError("Invalid credentials.")
        else:
            raise serializers.ValidationError("Must include email and password.")

        return data
## serializer for user profile

class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = '__all__'
        read_only_fields = ['user']