from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (CategoryViewSet, CommentViewSet, CustomTokenObtainView,
                    GenreViewSet, ReviewViewSet, SignUpAPIView, TitleViewSet,
                    UserViewSet)

app_name = "api"

router = DefaultRouter()

router.register("titles", TitleViewSet)
router.register("genres", GenreViewSet)
router.register("categories", CategoryViewSet)
router.register(
    r"titles/(?P<title_id>\d+)/reviews", ReviewViewSet, basename="reviews"
)
router.register(
    r"titles/(?P<title_id>\d+)/reviews/(?P<review_id>\d+)/comments",
    CommentViewSet,
    basename="comments",
)
router.register("users", UserViewSet, basename="users")

urlpatterns = [
    path("v1/", include(router.urls)),
    path("v1/auth/signup/", SignUpAPIView.as_view()),
    path(
        "v1/auth/token/",
        CustomTokenObtainView.as_view(),
        name="token_obtain_pair",
    ),
]
