import re

from rest_framework import serializers

from gifts.models import Gift
from gifts.serializers import GiftSerializer
from .models import Guest, GiftSelection
from .services import GuestService


class PublicGuestSerializer(serializers.ModelSerializer):
    """
    Dados expostos a quem informa o código do convite.
    Não inclui telefone nem outros dados pessoais além do nome.
    """
    class Meta:
        model = Guest
        fields = ['uuid', 'name', 'confirmed']
        read_only_fields = fields


class GiftBriefSerializer(serializers.ModelSerializer):
    """Serializer resumido do gift (para mostrar dentro do guest)"""
    class Meta:
        model = Gift
        fields = ['uuid', 'name', 'description', 'link']


class GuestSerializer(serializers.ModelSerializer):
    """
    Serializer de Guest.

    Input (criação/atualização):
    {
        "name": "Gabriel",
        "age": "adult",
        "category": "family",
        "phone": "(11) 9 9999-9999",
        "invite": "uuid-do-invite",
        "gifts": [
            {"gift": "uuid-do-gift", "message": "Parabéns!"},
            {"gift": "uuid-do-outro-gift"}
        ]
    }

    Output (leitura):
    {
        "uuid": "guest-123...",
        "name": "Gabriel",
        "age": "adult",
        "category": "family",
        "phone": "(11) 9 9999-9999",
        "confirmed": false,
        "invite": "uuid-do-invite",
        "gifts": [
            {
                "gift": {"uuid": "...", "name": "Carrinho", ...},
                "message": "Parabéns!",
                "selected_at": "2026-11-01T10:30:00Z"
            }
        ]
    }
    """

    # Campo de entrada: aceita lista de dicts {gift: uuid, message: string}
    gifts = serializers.ListField(
        child=serializers.DictField(),
        write_only=True,
        required=False,
        help_text="Lista de gifts escolhidos: [{'gift': uuid, 'message': string}]"
    )

    class Meta:
        model = Guest
        fields = ['uuid', 'name', 'age', 'phone', 'confirmed', 'category', 'invite', 'gifts']
        read_only_fields = ['uuid', 'confirmed']  # confirmed muda via evento, não direto

    def validate_phone(self, value):
        """Valida formato do telefone: (99) 9 9999-9999"""
        if not value:
            return value

        pattern = r'^\(\d{2}\) \d \d{4}-\d{4}$'
        if not re.match(pattern, value):
            raise serializers.ValidationError(
                "Formato de telefone inválido. Use: (99) 9 9999-9999"
            )
        return value

    def validate_gifts(self, value):
        """Valida a estrutura de cada item da lista de gifts"""
        if not value:
            return value

        for item in value:
            if not isinstance(item, dict):
                raise serializers.ValidationError("Cada gift deve ser um objeto")

            if 'gift' not in item:
                raise serializers.ValidationError("Cada gift deve ter o campo 'gift' (UUID)")

            # Valida que o gift existe
            try:
                Gift.objects.get(uuid=item['gift'])
            except Gift.DoesNotExist:
                raise serializers.ValidationError(f"Gift {item['gift']} não encontrado")

            # Valida que message é string (se existir)
            if 'message' in item and not isinstance(item['message'], str):
                raise serializers.ValidationError("O campo 'message' deve ser uma string")

        return value

    def to_representation(self, instance):
        """Customiza o output para incluir os gifts com mensagens e detalhes"""
        data = super().to_representation(instance)

        # Busca as seleções com os gifts relacionados (otimizado com select_related)
        selections = GiftSelection.objects.filter(guest=instance).select_related('gift')

        gifts_output = []
        for selection in selections:
            gifts_output.append({
                'gift': GiftBriefSerializer(selection.gift).data,
                'message': selection.message,
                'selected_at': selection.selected_at,
            })

        data['gifts'] = gifts_output
        return data

    def create(self, validated_data):
        """Cria um guest e processa os gifts escolhidos"""
        gifts_data = validated_data.pop('gifts', [])
        guest = Guest.objects.create(**validated_data)
        self._process_gifts(guest, gifts_data)
        return guest

    def update(self, instance, validated_data):
        """Atualiza um guest e reprocessa os gifts"""
        gifts_data = validated_data.pop('gifts', None)

        # Atualiza os campos básicos
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        # Se gifts foi enviado, reprocessa (substitui todas as seleções)
        if gifts_data is not None:
            GiftSelection.objects.filter(guest=instance).delete()
            self._process_gifts(instance, gifts_data)

        return instance

    def _process_gifts(self, guest, gifts_data):
        """Processa a lista de gifts escolhidos (cria as GiftSelections)"""
        for gift_data in gifts_data:
            gift_uuid = gift_data.get('gift')
            message = gift_data.get('message', '')

            gift = Gift.objects.get(uuid=gift_uuid)

            # Valida o limit via service
            GuestService.validate_gift_selection(guest, gift)

            # Cria a seleção
            GiftSelection.objects.create(
                guest=guest,
                gift=gift,
                message=message
            )
