from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from .models import Guest
from .serializers import GuestSerializer


class GuestViewSet(viewsets.ModelViewSet):
    """
    CRUD de Guests.
    Apenas usuários autenticados (pais) podem acessar.
    """
    queryset = Guest.objects.all()
    serializer_class = GuestSerializer
    lookup_field = 'uuid'
    permission_classes = [IsAuthenticated]
