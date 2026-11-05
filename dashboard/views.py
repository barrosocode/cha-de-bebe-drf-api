from drf_spectacular.utils import extend_schema
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .serializers import DashboardSerializer
from .services import DashboardService


class DashboardView(APIView):
    """
    Resumo da página inicial do painel.

    Apenas usuários autenticados.
    """
    permission_classes = [IsAuthenticated]

    @extend_schema(responses={200: DashboardSerializer})
    def get(self, request):
        serializer = DashboardSerializer(DashboardService.build())
        return Response(serializer.data)
