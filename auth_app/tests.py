
from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework.test import APITestCase


class AuthenticationTests(APITestCase):
    def test_registration_success(self):
        data = {
            "fullname": "Test User",
            "email": "test@example.com",
            "password": "Test12345!",
            "repeated_password": "Test12345!",
        }
        response = self.client.post(
            reverse("registration"), data, format="json"
        )
        self.assertEqual(response.status_code, 201)
        self.assertTrue(
            User.objects.filter(email=data["email"]).exists()
        )

    def test_registration_password_mismatch(self):
        data = {
            "fullname": "Test User",
            "email": "test@example.com",
            "password": "Test12345!",
            "repeated_password": "AnderesPasswort123!",
        }
        response = self.client.post(
            reverse("registration"), data, format="json"
        )
        self.assertEqual(response.status_code, 400)

    def test_login_success(self):
        User.objects.create_user(
            username="test@example.com",
            email="test@example.com",
            password="Test12345!",
        )
        data = {
            "email": "test@example.com",
            "password": "Test12345!",
        }
        response = self.client.post(
            reverse("login"), data, format="json"
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn("token", response.data)

    def test_login_wrong_password(self):
        User.objects.create_user(
            username="test@example.com",
            email="test@example.com",
            password="Test12345!",
        )
        data = {
            "email": "test@example.com",
            "password": "Falsch123!",
        }
        response = self.client.post(
            reverse("login"), data, format="json"
        )
        self.assertEqual(response.status_code, 400)
