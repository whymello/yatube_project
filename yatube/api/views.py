from django.shortcuts import get_object_or_404
from rest_framework import filters, mixins, viewsets
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from drf_spectacular.utils import extend_schema_view, extend_schema

from posts.models import Comment, Follow, Group, Post
from .permissions import OwnerOrReadOnly
from .serializers import (
    CommentSerializer,
    FollowSerializer,
    GroupSerializer,
    PostSerializer,
)


@extend_schema_view(
    list=extend_schema(
        summary="Список постов",
        description=(
            "Возвращает список всех постов. При указании параметров limit и offset выдача "
            "работает с пагинацией."
        ),
        tags=["Posts"],
    ),
    create=extend_schema(
        summary="Создать пост",
        description="Добавляет новый пост в коллекцию постов. Анонимные запросы запрещены.",
        tags=["Posts"],
    ),
    retrieve=extend_schema(
        summary="Детали поста",
        description="Возвращает один пост по id.",
        tags=["Posts"],
    ),
    update=extend_schema(
        summary="Обновить пост",
        description=(
            "Обновляет один пост по id. Обновить пост может только автор поста. "
            "Анонимные запросы запрещены."
        ),
        tags=["Posts"],
    ),
    partial_update=extend_schema(
        summary="Частично обновить пост",
        description=(
            "Частично обновляет один пост по id. Обновить пост может только автор поста. "
            "Анонимные запросы запрещены."
        ),
        tags=["Posts"],
    ),
    destroy=extend_schema(
        summary="Удалить пост",
        description=(
            "Удаляет один пост по id. Удалить пост может только автор поста. "
            "Анонимные запросы запрещены."
        ),
        tags=["Posts"],
    ),
)
class PostViewSet(viewsets.ModelViewSet):
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    permission_classes = (OwnerOrReadOnly,)
    pagination_class = LimitOffsetPagination

    def perform_create(self, serializer):
        return serializer.save(author=self.request.user)


@extend_schema_view(
    list=extend_schema(
        summary="Список комментариев",
        description="Возвращает список всех комментариев к посту по post_id.",
        tags=["Comments"],
    ),
    create=extend_schema(
        summary="Создать комментарий",
        description=(
            "Добавляет новый комментарий к посту по post_id в коллекцию комментариев. "
            "Анонимные запросы запрещены."
        ),
        tags=["Comments"],
    ),
    retrieve=extend_schema(
        summary="Детали комментария",
        description="Возвращает один комментарий по id к посту по post_id.",
        tags=["Comments"],
    ),
    update=extend_schema(
        summary="Обновить комментарий",
        description=(
            "Обновляет один комментарий по id к посту по post_id. "
            "Обновить комментарий может только автор комментария. "
            "Анонимные запросы запрещены."
        ),
        tags=["Comments"],
    ),
    partial_update=extend_schema(
        summary="Частично обновить комментарий",
        description=(
            "Частично обновляет один комментарий по id к посту по post_id. "
            "Обновить комментарий может только автор комментария. "
            "Анонимные запросы запрещены."
        ),
        tags=["Comments"],
    ),
    destroy=extend_schema(
        summary="Удалить комментарий",
        description=(
            "Удаляет один комментарий по id к посту по post_id. "
            "Удалить комментарий может только автор комментария. "
            "Анонимные запросы запрещены."
        ),
        tags=["Comments"],
    ),
)
class CommentViewSet(viewsets.ModelViewSet):
    serializer_class = CommentSerializer
    permission_classes = (OwnerOrReadOnly,)

    def get_queryset(self):
        return Comment.objects.filter(post=self.kwargs["post_pk"])

    def perform_create(self, serializer) -> None:
        post = get_object_or_404(Post, id=self.kwargs["post_pk"])
        serializer.save(
            author=self.request.user,
            post=post,
        )


@extend_schema_view(
    list=extend_schema(
        summary="Список групп",
        description="Возвращает список всех групп.",
        tags=["Groups"],
    ),
    retrieve=extend_schema(
        summary="Детали группы",
        description="Возвращает детали одной группы по id.",
        tags=["Groups"],
    ),
)
class GroupViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Group.objects.all()
    serializer_class = GroupSerializer
    permission_classes = (IsAuthenticatedOrReadOnly,)


@extend_schema_view(
    list=extend_schema(
        summary="Список подписок",
        description=(
            "Возвращает список всех подписок пользователя, сделавшего запрос. "
            "Анонимные запросы запрещены."
        ),
        tags=["Follow"],
    ),
    create=extend_schema(
        summary="Создать подписку",
        description=(
            "Добавляет подписку пользователя от имени которого сделан запрос на пользователя "
            "переданного в теле запроса в коллекцию подписок. Анонимные запросы запрещены."
        ),
        tags=["Follow"],
    ),
)
class FollowViewSet(mixins.ListModelMixin, mixins.CreateModelMixin, viewsets.GenericViewSet):
    serializer_class = FollowSerializer
    filter_backends = (filters.SearchFilter,)
    search_fields = ("following__username",)

    def get_queryset(self):
        return Follow.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        return serializer.save(user=self.request.user)
