from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token
from rest_framework.test import APITestCase


class ChangePasswordTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='papai', password='senhaantiga')
        token = Token.objects.create(user=self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {token.key}')
        self.url = '/api/auth/change-password/'

    def test_changes_password(self):
        response = self.client.post(self.url, {
            'old_password': 'senhaantiga',
            'new_password': 'senhanova1',
            'new_password_confirmation': 'senhanova1',
        }, format='json')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['message'], 'Senha alterada com sucesso')
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password('senhanova1'))

    def test_rejects_wrong_old_password(self):
        response = self.client.post(self.url, {
            'old_password': 'errada123',
            'new_password': 'senhanova1',
            'new_password_confirmation': 'senhanova1',
        }, format='json')

        self.assertEqual(response.status_code, 400)
        self.assertIn('old_password', response.data)
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password('senhaantiga'))

    def test_rejects_mismatched_confirmation(self):
        response = self.client.post(self.url, {
            'old_password': 'senhaantiga',
            'new_password': 'senhanova1',
            'new_password_confirmation': 'outrasenha',
        }, format='json')

        self.assertEqual(response.status_code, 400)
        self.assertIn('new_password_confirmation', response.data)

    def test_rejects_short_password(self):
        response = self.client.post(self.url, {
            'old_password': 'senhaantiga',
            'new_password': 'curta',
            'new_password_confirmation': 'curta',
        }, format='json')

        self.assertEqual(response.status_code, 400)
        self.assertIn('new_password', response.data)

    def test_requires_authentication(self):
        self.client.credentials()
        response = self.client.post(self.url, {
            'old_password': 'senhaantiga',
            'new_password': 'senhanova1',
            'new_password_confirmation': 'senhanova1',
        }, format='json')

        self.assertEqual(response.status_code, 401)
