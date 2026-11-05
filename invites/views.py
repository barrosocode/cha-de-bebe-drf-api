from django.core.exceptions import ValidationError as DjangoValidationError
from django.shortcuts import get_object_or_404
from drf_spectacular.utils import extend_schema
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from guests.serializers import PublicGuestSerializer
from guests.services import GuestService

from .models import Invite
from .serializers import (
    ConfirmGuestsRequestSerializer,
    ConfirmGuestsResponseSerializer,
    InviteGuestsResponseSerializer,
    InviteSerializer,
)
from .services import InviteService


class InviteViewSet(viewsets.ModelViewSet):
    """
    CRUD de Invites.
    Apenas usuários autenticados (pais) podem acessar.
    """
    queryset = Invite.objects.all()
    serializer_class = InviteSerializer
    lookup_field = 'uuid'
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        name = serializer.validated_data.get('name')
        invite = InviteService.create_invite(name)
        serializer.instance = invite

    def perform_update(self, serializer):
        serializer.save()

    @extend_schema(responses={200: InviteGuestsResponseSerializer})
    @action(
        detail=False,
        methods=['get'],
        url_path=r'(?P<code>[A-Za-z0-9]{6})/guests',
        permission_classes=[AllowAny],
    )
    def guests_by_code(self, request, code=None):
        """
        Mostra os nomes dos convidados de um convite, sem login.

        Usado antes de confirmar presença e antes de registrar um presente,
        para a pessoa escolher quem, daquele convite, está agindo.

        URL: GET /api/invites/{code}/guests/
        """
        invite = get_object_or_404(Invite, code=code.upper())
        guests = invite.guests.all().order_by('name')
        return Response({
            'invite': {
                'name': invite.name,
                'code': invite.code,
            },
            'guests': PublicGuestSerializer(guests, many=True).data,
        })

    @extend_schema(
        request=ConfirmGuestsRequestSerializer,
        responses={200: ConfirmGuestsResponseSerializer},
    )
    @action(
        detail=False,
        methods=['post'],
        url_path=r'(?P<code>[A-Za-z0-9]{6})/confirm_guests',
        permission_classes=[AllowAny],
    )
    def confirm_guests(self, request, code=None):
        """
        Confirma a presença de convidados de um invite, sem login.

        URL: POST /api/invites/{code}/confirm_guests/
        Body: {"guest_uuids": ["uuid-1", "uuid-2"]}

        A resposta devolve os nomes dos convidados daquele convite.
        Para listar os nomes antes de confirmar, use GET /api/invites/{code}/guests/.
        """
        invite = get_object_or_404(Invite, code=code.upper())

        guest_uuids = request.data.get('guest_uuids', [])
        if not guest_uuids or not isinstance(guest_uuids, list):
            return Response(
                {'error': 'guest_uuids deve ser uma lista não vazia'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            guests = invite.guests.filter(uuid__in=guest_uuids)
            if guests.count() != len(set(guest_uuids)):
                return Response(
                    {'error': 'Um ou mais convidados não pertencem a este convite'},
                    status=status.HTTP_400_BAD_REQUEST
                )
        except (DjangoValidationError, ValueError):
            return Response(
                {'error': 'guest_uuids contém um UUID inválido'},
                status=status.HTTP_400_BAD_REQUEST
            )

        confirmed_count = GuestService.confirm_guests_for_invite(invite, guest_uuids)
        guests = invite.guests.all().order_by('name')

        return Response({
            'message': f'{confirmed_count} convidado(s) confirmado(s) com sucesso',
            'confirmed_count': confirmed_count,
            'guests': PublicGuestSerializer(guests, many=True).data,
        })
