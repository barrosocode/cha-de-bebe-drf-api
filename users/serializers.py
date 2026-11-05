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


class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(write_only=True)
    new_password = serializers.CharField(
        write_only=True,
        min_length=8,
        error_messages={
            'min_length': 'A nova senha deve ter no mínimo 8 caracteres.',
        },
    )
    new_password_confirmation = serializers.CharField(write_only=True)

    def validate_old_password(self, value):
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError('Senha atual incorreta.')
        return value

    def validate(self, data):
        if data['new_password'] != data['new_password_confirmation']:
            raise serializers.ValidationError({
                'new_password_confirmation': 'A confirmação não confere com a nova senha.',
            })
        return data

    def save(self, **kwargs):
        user = self.context['request'].user
        user.set_password(self.validated_data['new_password'])
        user.save(update_fields=['password'])
        return user
