from django.core.exceptions import ValidationError

from guests.services import GuestService

from .models import Invite


class InviteService:
    @staticmethod
    def create_invite(name):
        """
        Cria um novo invite.

        O código é gerado automaticamente pelo model no save().
        Por enquanto é um wrapper simples, mas é aqui que entrará
        lógica adicional no futuro (ex: notificações, limites, etc).
        """
        if not name or not name.strip():
            raise ValidationError("O nome do convite é obrigatório")

        invite = Invite.objects.create(name=name.strip())
        return invite

    @staticmethod
    def confirm_guests(invite, guest_uuids):
        """
        Confirma a presença de múltiplos guests de um invite.

        invite: instância de Invite
        guest_uuids: lista de UUIDs dos guests que devem ser confirmados

        Retorna a quantidade de guests confirmados.
        """
        return GuestService.confirm_guests_for_invite(invite, guest_uuids)
