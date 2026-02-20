from django.contrib.auth import get_user_model
from rest_framework import serializers
from rest_framework import status

from posts.models import Comment, Follow, Group, Post

User = get_user_model()


class PostSerializer(serializers.ModelSerializer):
    author = serializers.SlugRelatedField(slug_field="username", read_only=True)

    class Meta:
        model = Post
        fields = ("id", "text", "pub_date", "author", "image", "group")
        read_only_fields = ("id", "pub_date")


class CommentSerializer(serializers.ModelSerializer):
    author = serializers.SlugRelatedField(read_only=True, slug_field="username")

    class Meta:
        model = Comment
        fields = ("id", "author", "post", "text", "created")
        read_only_fields = ("id", "created", "post")


class GroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = Group
        fields = ("id", "title", "slug", "description")


class FollowSerializer(serializers.ModelSerializer):
    user = serializers.SlugRelatedField(read_only=True, slug_field="username")
    following = serializers.SlugRelatedField(queryset=User.objects.all(), slug_field="username")

    class Meta:
        model = Follow
        fields = ("user", "following")

    def validate(self, attrs):
        user = self.context["request"].user
        following = attrs["following"]

        if user == following:
            raise serializers.ValidationError(detail="Нельзя подписаться на самого себя!")

        follow = Follow.objects.filter(user=user, following=following)

        if follow:
            raise serializers.ValidationError(
                detail="Вы уже подписаны на этого пользователя!", code=status.HTTP_400_BAD_REQUEST
            )

        return attrs
