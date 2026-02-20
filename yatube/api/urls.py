from django.urls import include, path
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularRedocView,
    SpectacularSwaggerView,
)
from rest_framework.routers import DefaultRouter
from rest_framework_nested.routers import NestedDefaultRouter

from .views import CommentViewSet, FollowViewSet, GroupViewSet, PostViewSet

router = DefaultRouter()
router.register(prefix="posts", viewset=PostViewSet)
router.register(prefix="groups", viewset=GroupViewSet)
router.register(prefix="follow", viewset=FollowViewSet, basename="follow")

posts_router = NestedDefaultRouter(parent_router=router, parent_prefix="posts", lookup="post")
posts_router.register(prefix="comments", viewset=CommentViewSet, basename="comment")


urlpatterns = [
    path("v1/", include(arg=router.urls)),
    path("v1/", include(arg=posts_router.urls)),
    path("v1/", include(arg="djoser.urls.jwt")),
]

urlpatterns += [
    # * YAML схема
    path("swagger/", SpectacularAPIView.as_view(), name="schema"),
    # * Swagger UI
    path(
        "swagger/ui/",
        SpectacularSwaggerView.as_view(url_name="schema"),
        name="swagger-ui",
    ),
    # * Redoc
    path(
        "redoc/",
        SpectacularRedocView.as_view(url_name="schema"),
        name="redoc",
    ),
]
