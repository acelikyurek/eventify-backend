from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth.models import User

class AuthenticationTests(APITestCase):

    def test_register_creates_user(self):
        url = "/api/auth/register"
        data = {"username": "alice", "email": "alice@example.com", "password": "strongpass"}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(User.objects.filter(username="alice").exists())

    def test_register_duplicate_email(self):
        User.objects.create_user(username="bob", email="bob@example.com", password="12345678")
        url = "/api/auth/register"
        data = {"username": "bob2", "email": "bob@example.com", "password": "strongpass"}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_login_returns_jwt(self):
        User.objects.create_user(username="carol", email="carol@example.com", password="secret123")
        url = "/api/auth/login"
        data = {"username": "carol", "password": "secret123"}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access", response.data)
        self.assertIn("refresh", response.data)
        