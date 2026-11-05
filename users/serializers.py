# Imports
from rest_framework import serializers
from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'first_name']
        read_only_fields = ['id']

class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        from django.contrib.auth import authenticate

        user = authenticate(
            username=data.get('username'),
            password=data.get('password'),
        )

        if not user:
            raise serializers.ValidationError('Login ou senha incorretos')

        if not user.is_active:
            raise serializers.ValidationError('Usuário inativo')

        data['user'] = user
        return data


class LoginResponseSerializer(serializers.Serializer):
    token = serializers.CharField(read_only=True)
    user = UserSerializer(read_only=True)


class LogoutResponseSerializer(serializers.Serializer):
    message = serializers.CharField(read_only=True)
