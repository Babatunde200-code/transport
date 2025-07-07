from rest_framework import serializers
from django.core.mail import send_mail
from django.contrib.auth import authenticate
from .models import CustomUser
from .models import UserProfile

class SignupSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'password', 'phone_number']
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        user = CustomUser.objects.create_user(**validated_data)
        code = user.generate_verification_code()
        send_mail(
            subject="Verify your account",
            message=f"Your verification code is: {code}",
            from_email="no-reply@travelshare.com",
            recipient_list=[user.email],
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
        user = authenticate(username=data['email'], password=data['password'])
        if not user:
            raise serializers.ValidationError("Invalid credentials")
        if not user.is_verified:
            raise serializers.ValidationError("Account not verified")
        return {'user': user}
    
## serializer for user profile

class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = '__all__'
        read_only_fields = ['user']