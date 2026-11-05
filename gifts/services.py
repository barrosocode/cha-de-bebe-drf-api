from django.core.exceptions import ValidationError
from .models import Gift, Tag


class GiftService:
    @staticmethod
    def validate_limit(gift_data, gift_instance=None):
        """
        Valida se o limit é válido.

        gift_data: dict com os dados do gift (incluindo 'limit')
        gift_instance: instância do gift (para atualizações)

        Na atualização, o limite não pode ficar abaixo da quantidade
        de compras já registradas para o presente.
        """
        limit = gift_data.get('limit')

        if limit is not None and limit <= 0:
            raise ValidationError("O limite deve ser maior que zero")

        if gift_instance is not None and limit is not None:
            purchased = gift_instance.giftselection_set.count()
            if limit < purchased:
                raise ValidationError(
                    "O limite não pode ser menor que a quantidade "
                    f"de itens já comprados ({purchased})"
                )

    @staticmethod
    def create_or_get_tag(tag_name):
        """
        Cria uma tag se não existir, ou retorna a existente.
        Garante que o nome esteja em uppercase.
        """
        tag_name = tag_name.strip().upper()
        tag, created = Tag.objects.get_or_create(
            name=tag_name,
            defaults={'description': ''}
        )
        return tag
