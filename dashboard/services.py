from gifts.models import Gift
from guests.models import GiftSelection, Guest
from invites.models import Invite

RECENT_RESERVATIONS_LIMIT = 5


def _rate(part, total):
    if total == 0:
        return 0.0
    return round(part * 100 / total, 1)


class DashboardService:
    @staticmethod
    def build():
        total_guests = Guest.objects.count()
        confirmed_guests = Guest.objects.filter(confirmed=True).count()
        total_gifts = Gift.objects.count()
        reserved_gifts = GiftSelection.objects.values('gift_id').distinct().count()

        recent = (
            GiftSelection.objects
            .select_related('guest', 'gift')
            .order_by('-selected_at')[:RECENT_RESERVATIONS_LIMIT]
        )

        return {
            'total_invites': Invite.objects.count(),
            'total_guests': total_guests,
            'confirmed_guests': confirmed_guests,
            'confirmation_rate': _rate(confirmed_guests, total_guests),
            'total_gifts': total_gifts,
            'reserved_gifts': reserved_gifts,
            'reservation_rate': _rate(reserved_gifts, total_gifts),
            'recent_reservations': [
                {
                    'guest_name': selection.guest.name,
                    'gift_name': selection.gift.name,
                    'message': selection.message,
                    'reserved_at': selection.selected_at,
                }
                for selection in recent
            ],
        }
