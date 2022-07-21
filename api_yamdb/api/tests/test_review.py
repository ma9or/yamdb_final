from django.shortcuts import get_object_or_404
from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient
from reviews.models import Review
from titles.models import Category, Genre, Title
from users.models import User

TEST_USER_FIELDS: dict = {"username": "auth", "role": "user"}

TEST_ADMIN_USER_FIELDS: dict = {"username": "admin", "role": "admin"}

TEST_GENRE_FIELDS: dict = {"name": "Ужасы", "slug": "horror"}

TEST_CATEGORY_FIELDS: dict = {"name": "Фильм", "slug": "films"}


class ReviewViewsTest(TestCase):
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

    def setUp(self):
        self.client = APIClient()
        self.authorized_client = APIClient()
        self.authorized_client.force_authenticate(self.user)
        self.admin_client = APIClient()
        self.admin_client.force_authenticate(self.admin_user)

    def test_new_title_added(self):
        title_count = Title.objects.count()
        self.assertEqual(title_count, 1)

    def test_new_review_added(self):
        review_count = Review.objects.count()
        self.assertEqual(review_count, 1)

    def test_new_reviews_added_to_title(self):
        data = {"text": "Отзыв №2", "score": 3}
        response = self.authorized_client.post(
            f"/api/v1/titles/{self.title.id}/reviews/", data=data
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        title = get_object_or_404(Title, pk=1)
        self.assertEqual(title.rating, 4)

    def test_get_review_detail_nonauthorized(self):
        response = self.client.get(
            f"/api/v1/titles/{self.title.id}/reviews/{self.review.id}/"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
