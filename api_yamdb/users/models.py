from django.contrib.auth.models import AbstractUser
from django.db import models

ROLE_CHOICES = (
    ("user", "user"),
    ("admin", "admin"),
    ("moderator", "moderator"),
)


class User(AbstractUser):
    bio = models.TextField(
        "Биография",
        blank=True,
    )
    role = models.CharField(max_length=100, choices=ROLE_CHOICES)
