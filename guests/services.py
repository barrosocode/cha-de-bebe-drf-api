from django.core.exceptions import ValidationError

from .models import GiftSelection


class GuestService:
    @staticmethod
    def validate_gift_selection(guest, gift):
        """
        Valida se um guest pode escolher um gift.

        O mesmo convidado pode escolher o mesmo presente mais de uma vez.
        Cada escolha conta para o limite do presente.
        """
        # Conta quantos guests já escolheram este gift
        current_selections = GiftSelection.objects.filter(gift=gift).count()

        if current_selections >= gift.limit:
            raise ValidationError(
                f"O gift '{gift.name}' já atingiu o limite de {gift.limit} escolhas"
            )

    @staticmethod
    def confirm_guests_for_invite(invite, guest_uuids):
        """
        Confirma a presença de múltiplos guests de um invite.

        invite: instância de Invite
        guest_uuids: lista de UUIDs dos guests que devem ser confirmados

        Retorna a quantidade de guests confirmados.
        """
        guests = invite.guests.filter(uuid__in=guest_uuids)
        confirmed_count = 0

        for guest in guests:
            if not guest.confirmed:
                guest.confirm_presence()
                confirmed_count += 1

        return confirmed_count
