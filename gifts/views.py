from django.core.exceptions import ValidationError as DjangoValidationError
from django.db import transaction
from django.db.models import Count, F
from drf_spectacular.utils import extend_schema
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError as DRFValidationError
from rest_framework.permissions import AllowAny, IsAuthenticatedOrReadOnly
from rest_framework.response import Response

from guests.services import GuestService
from invites.models import Invite

from .models import File, Gift, Tag
from .serializers import (
    FileSerializer,
    GiftPurchaseResponseSerializer,
    GiftPurchaseSerializer,
    GiftSerializer,
    TagSerializer,
)
from .services import GiftService


class GiftViewSet(viewsets.ModelViewSet):
    """
    CRUD completo de Gifts.

    Leitura (listar e detalhar) é pública.
    Quem não está logado só vê, na listagem, presentes ainda disponíveis
    (quantidade de compras menor que o limite).
    Criar, editar e apagar exigem login.

    Endpoints gerados automaticamente:
    - GET /api/gifts/ → lista (pública: só disponíveis; autenticada: todos)
    - POST /api/gifts/ → cria um novo
    - GET /api/gifts/{uuid}/ → detalhes de um
    - PUT /api/gifts/{uuid}/ → atualiza completo
    - PATCH /api/gifts/{uuid}/ → atualiza parcial
    - DELETE /api/gifts/{uuid}/ → deleta
    - POST /api/gifts/{uuid}/purchase/ → convidado escolhe o presente sem login
    """
    queryset = Gift.objects.all()
    serializer_class = GiftSerializer
    lookup_field = 'uuid'  # Usa UUID em vez de ID
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        queryset = super().get_queryset()
        if self.action == 'list' and not self.request.user.is_authenticated:
            queryset = queryset.annotate(
                purchased_count=Count('giftselection'),
            ).filter(purchased_count__lt=F('limit'))
        return queryset

    def perform_create(self, serializer):
        """Hook chamado antes de salvar um novo gift"""
        # Valida o limit via service
        try:
            GiftService.validate_limit(serializer.validated_data)
        except DjangoValidationError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

        serializer.save()

    def perform_update(self, serializer):
        """Hook chamado antes de atualizar um gift"""
        try:
            GiftService.validate_limit(
                serializer.validated_data,
                gift_instance=serializer.instance
            )
        except DjangoValidationError as exc:
            messages = getattr(exc, 'messages', None) or [str(exc)]
            raise DRFValidationError({'limit': messages})

        serializer.save()

    @extend_schema(
        request=GiftPurchaseSerializer,
        responses={201: GiftPurchaseResponseSerializer},
    )
    @action(
        detail=True,
        methods=['post'],
        url_path='purchase',
        permission_classes=[AllowAny],
    )
    def purchase(self, request, uuid=None):
        """
        Registra a escolha de um presente sem login.

        O convidado informa o código do convite, escolhe qual pessoa
        daquele convite está dando o presente e pode deixar uma mensagem.

        URL: POST /api/gifts/{uuid}/purchase/
        Body: {"code": "ABC123", "guest": "uuid-do-convidado", "message": "Com carinho"}

        Os nomes para a escolha vêm de GET /api/invites/{code}/guests/.
        """
        gift = self.get_object()
        serializer = GiftPurchaseSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        code = serializer.validated_data['code']
        guest_uuid = serializer.validated_data['guest']
        message = serializer.validated_data.get('message', '')

        invite = Invite.objects.filter(code=code).first()
        if invite is None:
            return Response(
                {'error': 'Convite não encontrado'},
                status=status.HTTP_404_NOT_FOUND,
            )

        guest = invite.guests.filter(uuid=guest_uuid).first()
        if guest is None:
            return Response(
                {'error': 'Convidado não pertence a este convite'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            with transaction.atomic():
                GuestService.validate_gift_selection(guest, gift)
                selection = gift.giftselection_set.create(
                    guest=guest,
                    message=message,
                )
        except DjangoValidationError as exc:
            detail = exc.messages[0] if getattr(exc, 'messages', None) else str(exc)
            return Response({'error': detail}, status=status.HTTP_400_BAD_REQUEST)

        return Response(
            {
                'message': 'Presente registrado com sucesso',
                'guest': {'uuid': guest.uuid, 'name': guest.name},
                'gift_message': selection.message,
                'selected_at': selection.selected_at,
            },
            status=status.HTTP_201_CREATED,
        )


class TagViewSet(viewsets.ModelViewSet):
    """
    CRUD de Tags.

    Listar e detalhar é público. Criar, editar e apagar exigem login.
    """
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    lookup_field = 'uuid'
    permission_classes = [IsAuthenticatedOrReadOnly]


class FileViewSet(viewsets.ModelViewSet):
    """
    CRUD de Files (se precisar gerenciar arquivos independentemente).
    """
    queryset = File.objects.all()
    serializer_class = FileSerializer
    lookup_field = 'uuid'
