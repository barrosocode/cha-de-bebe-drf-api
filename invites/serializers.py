from rest_framework import serializers

from guests.serializers import PublicGuestSerializer

from .models import Invite


class InviteSerializer(serializers.ModelSerializer):
    """
    Serializer de Invite.

    O campo 'code' é gerado automaticamente pelo model, então é read_only.
    O usuário só precisa enviar o 'name' na criação.
    """

    class Meta:
        model = Invite
        fields = ['uuid', 'name', 'code']
        read_only_fields = ['uuid', 'code']


class InviteCodeSummarySerializer(serializers.Serializer):
    name = serializers.CharField()
    code = serializers.CharField()


class InviteGuestsResponseSerializer(serializers.Serializer):
    """Resposta de GET /api/invites/{code}/guests/."""
    invite = InviteCodeSummarySerializer()
    guests = PublicGuestSerializer(many=True)


class ConfirmGuestsRequestSerializer(serializers.Serializer):
    """Corpo de POST /api/invites/{code}/confirm_guests/."""
    guest_uuids = serializers.ListField(
        child=serializers.UUIDField(),
        allow_empty=False,
    )


class ConfirmGuestsResponseSerializer(serializers.Serializer):
    """Resposta de POST /api/invites/{code}/confirm_guests/."""
    message = serializers.CharField()
    confirmed_count = serializers.IntegerField()
    guests = PublicGuestSerializer(many=True)
