import unittest

from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient
from users.models import User


class UsersViewsTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(username="authorized_user")
        cls.guest_client = APIClient()
        cls.authorized_client = APIClient()
        cls.authorized_client.force_authenticate(cls.user)
        cls.admin_user = User.objects.create_user(
            username="admin_user", role="admin"
        )
        cls.admin_client = APIClient()
        cls.admin_client.force_authenticate(cls.admin_user)

    def test_cool_test(self):
        """cool test"""
        self.assertEqual(True, True)

    def test_get_users_list(self):
        """Получение списка всех пользователей.
        Права доступа: Администратор."""
        url = "/api/v1/users/"
        User.objects.create_user(username="testusername")
        response = self.admin_client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response.json(),
            {
                "count": 3,
                "next": None,
                "previous": None,
                "results": [
                    {
                        "username": "authorized_user",
                        "email": "",
                        "first_name": "",
                        "last_name": "",
                        "bio": "",
                        "role": "",
                    },
                    {
                        "username": "admin_user",
                        "email": "",
                        "first_name": "",
                        "last_name": "",
                        "bio": "",
                        "role": "admin",
                    },
                    {
                        "username": "testusername",
                        "email": "",
                        "first_name": "",
                        "last_name": "",
                        "bio": "",
                        "role": "",
                    },
                ],
            },
        )

    def test_get_users_list_by_not_admin(self):
        """Не админ не может получить список всех пользователей."""
        url = "/api/v1/users/"
        response = self.authorized_client.get(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(
            response.json(),
            {"detail": "You do not have permission to perform this action."},
        )

    def test_get_users_detail(self):
        """Получение пользователя по username.
        Права доступа: Администратор."""
        url = f"/api/v1/users/{self.user.username}/"
        response = self.admin_client.get(url)
        self.assertEqual(
            User.objects.filter(username=self.user.username).exists(), True
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response.json(),
            {
                "username": "authorized_user",
                "email": "",
                "first_name": "",
                "last_name": "",
                "bio": "",
                "role": "",
            },
        )

    def test_create_user(self):
        """Добавление пользователя.
        Права доступа: Администратор."""
        url = "/api/v1/users/"
        data = {
            "username": "string",
            "email": "user@example.com",
            "first_name": "string",
            "last_name": "string",
            "bio": "string",
            "role": "user",
        }
        response = self.admin_client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.json(), data)

    def test_create_user_with_invalid_data(self):
        """Добавление пользователя с невалидными данными."""
        url = "/api/v1/users/"
        data = {}
        response = self.admin_client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.json(),
            {
                "email": ["This field is required."],
                "username": ["This field is required."],
            },
        )
        data = {
            "first_name": "string",
            "last_name": "string",
            "bio": "string",
            "role": "user",
        }
        response = self.admin_client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.json(),
            {
                "email": ["This field is required."],
                "username": ["This field is required."],
            },
        )
        data = {"username": "string"}
        response = self.admin_client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.json(), {"email": ["This field is required."]}
        )
        data = {"email": "user@example.com"}
        response = self.admin_client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.json(), {"username": ["This field is required."]}
        )

    def test_create_user_by_superuser(self):
        """Добавление пользователя by superuser."""
        staff_user = User.objects.create_user(username="staff_user")
        staff_user.is_staff = True
        staff_user.save(update_fields=["is_staff"])
        staffser_client = APIClient()
        staffser_client.force_authenticate(staff_user)
        url = "/api/v1/users/"
        data = {
            "username": "string",
            "email": "user@example.com",
            "first_name": "string",
            "last_name": "string",
            "bio": "string",
            "role": "user",
        }
        response = staffser_client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.json(), data)

    def test_patch_users_detail(self):
        """Изменение данных пользователя по username.
        Права доступа: Администратор."""
        user = User.objects.create_user(
            username="testusername",
            email="user@example.com",
        )
        url = f"/api/v1/users/{user.username}/"
        data = {
            "username": "new_testusername",
            "email": "new_user@example.com",
            "first_name": "string",
            "last_name": "string",
            "bio": "string",
            "role": "moderator",
        }
        response = self.admin_client.patch(url, data)
        self.assertEqual(
            User.objects.filter(username=self.user.username).exists(), True
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json(), data)

    def test_patch_users_detail_role(self):
        """Поменять только роль пользователя.
        Права доступа: Администратор."""
        user = User.objects.create_user(
            username="testusername",
            email="user@example.com",
        )
        url = f"/api/v1/users/{user.username}/"
        data = {
            "role": "moderator",
        }
        response = self.admin_client.patch(url, data)
        self.assertEqual(
            User.objects.filter(username=self.user.username).exists(), True
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        test_json = {
            "username": "testusername",
            "email": "user@example.com",
            "first_name": "",
            "last_name": "",
            "bio": "",
            "role": "moderator",
        }
        self.assertEqual(response.json(), test_json)

    def test_patch_users_detail_invalid_role(self):
        """Нельзя поменять роль пользователя на произвольное значение.
        Права доступа: Администратор."""
        user = User.objects.create_user(
            username="testusername",
            email="user@example.com",
        )
        url = f"/api/v1/users/{user.username}/"
        data = {
            "role": "admiral",
        }
        response = self.admin_client.patch(url, data)
        self.assertEqual(
            User.objects.filter(username=self.user.username).exists(), True
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        test_json = {"role": ['"admiral" is not a valid choice.']}
        self.assertEqual(response.json(), test_json)

    def test_get_users_me(self):
        """Получение данных своей учетной записи.
        Права доступа: Любой авторизованный пользователь."""
        url = "/api/v1/users/me/"
        response = self.authorized_client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response.json(),
            {
                "username": "authorized_user",
                "email": "",
                "first_name": "",
                "last_name": "",
                "bio": "",
                "role": "",
            },
        )

    def test_patch_users_me(self):
        """Изменение данных своей учетной записи.
        Права доступа: Любой авторизованный пользователь.
        менять свое имя и майл можно на уникальные значения"""
        url = "/api/v1/users/me/"
        data = {
            "first_name": "New user first name",
            "last_name": "New user last name",
            "bio": "new user bio",
        }
        response = self.authorized_client.patch(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        test_json = {
            "username": "authorized_user",
            "email": "",
            "first_name": "New user first name",
            "last_name": "New user last name",
            "bio": "new user bio",
            "role": "",
        }
        self.assertEqual(response.json(), test_json)
        # поменяем email c "" на "test@mail.ru"
        data = {
            "email": "test@mail.ru",
            "first_name": "New user first name",
            "last_name": "New user last name",
            "bio": "new user bio",
        }
        response = self.authorized_client.patch(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        test_json = {
            "username": "authorized_user",
            "email": "test@mail.ru",
            "first_name": "New user first name",
            "last_name": "New user last name",
            "bio": "new user bio",
            "role": "",
        }
        self.assertEqual(response.json(), test_json)
        # поменяем email c "test@mail.ru" на "test_1@mail.ru"
        data = {
            "email": "test_1@mail.ru",
            "first_name": "New user first name",
            "last_name": "New user last name",
            "bio": "new user bio",
        }
        response = self.authorized_client.patch(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        test_json = {
            "username": "authorized_user",
            "email": "test_1@mail.ru",
            "first_name": "New user first name",
            "last_name": "New user last name",
            "bio": "new user bio",
            "role": "",
        }
        self.assertEqual(response.json(), test_json)
        # поменяем username c "authorized_user" на "authorized_user_1"
        data = {
            "username": "authorized_user_1",
            "first_name": "New user first name",
            "last_name": "New user last name",
            "bio": "new user bio",
        }
        response = self.authorized_client.patch(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        test_json = {
            "username": "authorized_user_1",
            "email": "test_1@mail.ru",
            "first_name": "New user first name",
            "last_name": "New user last name",
            "bio": "new user bio",
            "role": "",
        }
        self.assertEqual(response.json(), test_json)

    @unittest.expectedFailure
    def test_patch_users_me_role_by_user_expected_failure(self):
        """Изменение своей роли юзером"""
        user = User.objects.create_user(
            username="testusername",
            role="user",
        )
        user_client = APIClient()
        user_client.force_authenticate(user)
        url = "/api/v1/users/me/"
        data = {
            "role": "admin",
        }
        response = user_client.patch(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        test_json = {
            "username": "testusername",
            "email": "",
            "first_name": "",
            "last_name": "",
            "bio": "",
            "role": "admin",
        }
        self.assertEqual(response.json(), test_json)

    def test_patch_users_me_role_by_user(self):
        """Пользователь с ролью user не может сменить себе роль"""
        user = User.objects.create_user(
            username="testusername",
            role="user",
        )
        user_client = APIClient()
        user_client.force_authenticate(user)
        url = "/api/v1/users/me/"
        data = {
            "role": "admin",
        }
        response = user_client.patch(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        test_json = {
            "username": "testusername",
            "email": "",
            "first_name": "",
            "last_name": "",
            "bio": "",
            "role": "user",
        }
        self.assertEqual(response.json(), test_json)
