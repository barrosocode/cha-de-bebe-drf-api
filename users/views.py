# Imports
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from django.contrib.auth import logout

from drf_spectacular.utils import extend_schema

from users.serializers import (
    ChangePasswordSerializer,
    LoginResponseSerializer,
    LoginSerializer,
    LogoutResponseSerializer,
    UserSerializer,
)

# routes

# login
@extend_schema(request=LoginSerializer, responses={200: LoginResponseSerializer})
@api_view(['POST'])
@permission_classes([AllowAny])
def login_view(request):
    serializer = LoginSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    user = serializer.validated_data['user']
    token, created = Token.objects.get_or_create(user=user)
    return Response({
        'token': token.key,
        'user': UserSerializer(user).data,
    })

# logout
@extend_schema(request=None, responses={200: LogoutResponseSerializer})
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def logout_view(request):
    try:
        request.user.auth_token.delete()
    except:
        pass

    logout(request)
    return Response({'message': 'Logout realizado com sucesso'})

# me
@extend_schema(responses={200: UserSerializer})
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def me_view(request):
    serializer = UserSerializer(request.user)
    return Response(serializer.data)


# change password
@extend_schema(request=ChangePasswordSerializer, responses={200: LogoutResponseSerializer})
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def change_password_view(request):
    serializer = ChangePasswordSerializer(data=request.data, context={'request': request})
    serializer.is_valid(raise_exception=True)
    serializer.save()
    return Response({'message': 'Senha alterada com sucesso'})
