from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient
from reviews.models import Comment, Review
from titles.models import Category, Genre, Title
from users.models import User

TEST_USER_FIELDS: dict = {"username": "auth", "role": "user"}

TEST_ADMIN_USER_FIELDS: dict = {"username": "admin", "role": "admin"}

TEST_GENRE_FIELDS: dict = {"name": "Ужасы", "slug": "horror"}

TEST_CATEGORY_FIELDS: dict = {"name": "Фильм", "slug": "films"}


class CommentViewsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(**TEST_USER_FIELDS)
        cls.admin_user = User.objects.create_user(**TEST_ADMIN_USER_FIELDS)
        cls.genre = Genre.objects.create(**TEST_GENRE_FIELDS)
        cls.category = Category.objects.create(**TEST_CATEGORY_FIELDS)
        data = {
            "name": "Кошмар на улице Вязов",
            "year": 1984,
            "category": cls.category,
            "description": "Классика жанра",
        }
        cls.title = Title.objects.create(**data)
        cls.title.genre.set([cls.genre.id])
        data = {
            "title": cls.title,
            "text": "Отзыв №1",
            "score": 5,
            "author": cls.admin_user,
        }
        cls.review = Review.objects.create(**data)
        data = {
            "review": cls.review,
            "text": "Шедеврально",
            "author": cls.admin_user,
        }
        cls.comment = Comment.objects.create(**data)

    def setUp(self):
        self.client = APIClient()
        self.authorized_client = APIClient()
        self.authorized_client.force_authenticate(self.user)
        self.admin_client = APIClient()
        self.admin_client.force_authenticate(self.admin_user)

    def test_new_comment_added(self):
        self.assertEqual(Comment.objects.count(), 1)

    def test_get_comment(self):
        response = self.authorized_client.get(
            f"/api/v1/titles/{self.title.id}/"
            f"reviews/{self.review.id}/comments/"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_add_new_commit(self):
        data = {"text": "Djc[bnbntkmyj", "review": self.review.id}
        response = self.authorized_client.post(
            f"/api/v1/titles/{self.title.id}/"
            f"reviews/{self.review.id}/comments/",
            data=data,
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_not_add_bad_comment(self):
        data = {}
        response = self.authorized_client.post(
            f"/api/v1/titles/{self.title.id}/"
            f"reviews/{self.review.id}/comments/",
            data=data,
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
