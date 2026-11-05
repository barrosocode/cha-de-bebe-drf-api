from datetime import timedelta

from django.contrib.auth.models import User
from django.utils import timezone
from rest_framework.authtoken.models import Token
from rest_framework.test import APITestCase

from gifts.models import Gift
from guests.models import GiftSelection, Guest
from invites.models import Invite


class DashboardViewTests(APITestCase):
    def setUp(self):
        user = User.objects.create_user(username='pais', password='secret123')
        token = Token.objects.create(user=user)
        self.auth = {'HTTP_AUTHORIZATION': f'Token {token.key}'}

    def test_requires_authentication(self):
        response = self.client.get('/api/dashboard/')
        self.assertEqual(response.status_code, 401)

    def test_empty_dashboard_returns_zero_rates(self):
        response = self.client.get('/api/dashboard/', **self.auth)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, {
            'total_invites': 0,
            'total_guests': 0,
            'confirmed_guests': 0,
            'confirmation_rate': 0.0,
            'total_gifts': 0,
            'reserved_gifts': 0,
            'reservation_rate': 0.0,
            'recent_reservations': [],
        })

    def test_summary_counts_rates_and_recent_reservations(self):
        family = Invite.objects.create(name='Família')
        Invite.objects.create(name='Igreja')

        gabriel = Guest.objects.create(
            name='Gabriel',
            age='adult',
            category='family',
            invite=family,
            confirmed=True,
        )
        ana = Guest.objects.create(
            name='Ana',
            age='adult',
            category='family',
            invite=family,
            confirmed=True,
        )
        Guest.objects.create(
            name='Bruno',
            age='kid',
            category='friend',
            invite=family,
            confirmed=False,
        )

        gifts = [
            Gift.objects.create(
                name=f'Presente {index}',
                link='https://example.com/presente',
                limit=2,
            )
            for index in range(7)
        ]

        base = timezone.now()
        selections = [
            (gabriel, gifts[0], 'Mais antigo', base),
            (gabriel, gifts[1], '', base + timedelta(minutes=1)),
            (gabriel, gifts[2], '', base + timedelta(minutes=2)),
            (gabriel, gifts[3], '', base + timedelta(minutes=3)),
            (gabriel, gifts[4], '', base + timedelta(minutes=4)),
            (gabriel, gifts[5], '', base + timedelta(minutes=5)),
            (ana, gifts[0], 'Parabéns!', base + timedelta(minutes=6)),
        ]
        for guest, gift, message, selected_at in selections:
            selection = GiftSelection.objects.create(
                guest=guest,
                gift=gift,
                message=message,
            )
            GiftSelection.objects.filter(pk=selection.pk).update(selected_at=selected_at)

        response = self.client.get('/api/dashboard/', **self.auth)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['total_invites'], 2)
        self.assertEqual(response.data['total_guests'], 3)
        self.assertEqual(response.data['confirmed_guests'], 2)
        self.assertEqual(response.data['confirmation_rate'], 66.7)
        self.assertEqual(response.data['total_gifts'], 7)
        self.assertEqual(response.data['reserved_gifts'], 6)
        self.assertEqual(response.data['reservation_rate'], 85.7)

        recent = response.data['recent_reservations']
        self.assertEqual(
            [(item['guest_name'], item['gift_name'], item['message']) for item in recent],
            [
                ('Ana', 'Presente 0', 'Parabéns!'),
                ('Gabriel', 'Presente 5', ''),
                ('Gabriel', 'Presente 4', ''),
                ('Gabriel', 'Presente 3', ''),
                ('Gabriel', 'Presente 2', ''),
            ],
        )
        self.assertTrue(recent[0]['reserved_at'])
