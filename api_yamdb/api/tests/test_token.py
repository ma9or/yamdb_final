import unittest

from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.core import mail
from django.shortcuts import get_object_or_404
from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient
from users.models import User


class TokenViewsTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(username="authorized_client")
        cls.guest_client = APIClient()
        cls.authorized_client = APIClient()
        cls.authorized_client.force_authenticate(cls.user)

    def test_cool_test(self):
        """cool test"""
        self.assertEqual(True, True)

    @unittest.expectedFailure
    def test_auth_token_post(self):
        """Получение JWT-токена в обмен на username и confirmation code."""
        url = "/api/v1/auth/token/"
        User.objects.create_user(username="testusername")
        data = {"username": "testusername", "confirmation_code": 123456}
        response = self.guest_client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(type(response.json()), dict)
        self.assertEqual(len(response.json()), 1)

    def test_signup_create_user_check_confirmation_code(self):
        """Проверка кода подтверждения при регистрации пользователя."""
        url = "/api/v1/auth/signup/"
        user_count = User.objects.count()
        data = {"email": "test@mail.ru", "username": "testusername"}
        response = self.guest_client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        user = User.objects.get(id=user_count + 1)
        self.assertEqual(
            mail.outbox[0].subject, "Confirmation code for receiving a token"
        )
        self.assertEqual(type(mail.outbox[0].body), str)
        confirmation_code = mail.outbox[0].body
        PasswordResetTokenGenerator().check_token(user, confirmation_code)
        self.assertTrue(
            PasswordResetTokenGenerator().check_token(user, confirmation_code)
        )

    def test_auth_token_post_with_generated_confirmation_code(self):
        """Получение JWT-токена в обмен на username и сгенерированный
        confirmation code."""
        url = "/api/v1/auth/signup/"
        user_count = User.objects.count()
        data = {"email": "test@mail.ru", "username": "testusername"}
        response = self.guest_client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        user = User.objects.get(id=user_count + 1)
        self.assertEqual(type(mail.outbox[0].body), str)
        confirmation_code = mail.outbox[0].body
        PasswordResetTokenGenerator().check_token(user, confirmation_code)
        self.assertTrue(
            PasswordResetTokenGenerator().check_token(user, confirmation_code)
        )
        # получение токена
        url = "/api/v1/auth/token/"
        user = get_object_or_404(User, username="testusername")
        data = {
            "username": "testusername",
            "confirmation_code": confirmation_code,
        }
        response = self.guest_client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(type(response.json()), dict)
        self.assertEqual(len(response.json()), 1)
        self.assertTrue("token" in response.json())

    def test_auth_token_post_invalid_confirmation_code(self):
        """Получение JWT-токена c неверным confirmation code."""
        url = "/api/v1/auth/token/"
        User.objects.create_user(username="testusername")
        data = {"username": "testusername", "confirmation_code": 123456}
        response = self.guest_client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(type(response.json()), dict)
        self.assertEqual(
            response.json(),
            {"confirmation_code": ["Неверный код подтверждения"]},
        )

    def test_auth_token_post_without_username(self):
        """Получение JWT-токена без username."""
        url = "/api/v1/auth/signup/"
        user_count = User.objects.count()
        data = {"email": "test@mail.ru", "username": "testusername"}
        response = self.guest_client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        user = User.objects.get(id=user_count + 1)
        self.assertEqual(type(mail.outbox[0].body), str)
        confirmation_code = mail.outbox[0].body
        PasswordResetTokenGenerator().check_token(user, confirmation_code)
        self.assertTrue(
            PasswordResetTokenGenerator().check_token(user, confirmation_code)
        )
        # получение токена
        url = "/api/v1/auth/token/"
        user = get_object_or_404(User, username="testusername")
        data = {
            "confirmation_code": confirmation_code,
        }
        response = self.guest_client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
