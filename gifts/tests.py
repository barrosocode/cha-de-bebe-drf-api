from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token
from rest_framework.test import APITestCase

from guests.models import GiftSelection, Guest
from invites.models import Invite

from .models import Gift


class GiftListAvailabilityTests(APITestCase):
    def setUp(self):
        invite = Invite.objects.create(name='Família')
        self.guest = Guest.objects.create(
            name='Gabriel',
            age='adult',
            category='family',
            invite=invite,
        )
        self.available = Gift.objects.create(
            name='Disponível',
            link='https://example.com/disponivel',
            limit=2,
        )
        self.sold_out = Gift.objects.create(
            name='Esgotado',
            link='https://example.com/esgotado',
            limit=1,
        )
        GiftSelection.objects.create(guest=self.guest, gift=self.available)
        GiftSelection.objects.create(guest=self.guest, gift=self.sold_out)

        user = User.objects.create_user(username='pais', password='secret123')
        token = Token.objects.create(user=user)
        self.auth = {'HTTP_AUTHORIZATION': f'Token {token.key}'}

    def test_anonymous_list_returns_only_available_gifts(self):
        response = self.client.get('/api/gifts/')

        self.assertEqual(response.status_code, 200)
        names = [gift['name'] for gift in response.data]
        self.assertEqual(names, ['Disponível'])

    def test_authenticated_list_returns_sold_out_gifts(self):
        response = self.client.get('/api/gifts/', **self.auth)

        self.assertEqual(response.status_code, 200)
        names = sorted(gift['name'] for gift in response.data)
        self.assertEqual(names, ['Disponível', 'Esgotado'])


class GiftLimitUpdateTests(APITestCase):
    def setUp(self):
        invite = Invite.objects.create(name='Família')
        guest = Guest.objects.create(
            name='Gabriel',
            age='adult',
            category='family',
            invite=invite,
        )
        self.gift = Gift.objects.create(
            name='Jogo de panelas',
            link='https://example.com/panelas',
            limit=3,
        )
        GiftSelection.objects.create(guest=guest, gift=self.gift)
        GiftSelection.objects.create(guest=guest, gift=self.gift)

        user = User.objects.create_user(username='pais', password='secret123')
        token = Token.objects.create(user=user)
        self.auth = {'HTTP_AUTHORIZATION': f'Token {token.key}'}

    def test_rejects_limit_below_purchased_quantity(self):
        response = self.client.patch(
            f'/api/gifts/{self.gift.uuid}/',
            {'limit': 1},
            format='json',
            **self.auth,
        )

        self.assertEqual(response.status_code, 400)
        self.assertIn('já comprados (2)', response.data['limit'][0])
        self.gift.refresh_from_db()
        self.assertEqual(self.gift.limit, 3)

    def test_accepts_limit_equal_to_purchased_quantity(self):
        response = self.client.patch(
            f'/api/gifts/{self.gift.uuid}/',
            {'limit': 2},
            format='json',
            **self.auth,
        )

        self.assertEqual(response.status_code, 200)
        self.gift.refresh_from_db()
        self.assertEqual(self.gift.limit, 2)
