from django import forms

from .models import Post


class PostForm(forms.ModelForm):
    """Форма для создания и редактирования постов."""

    class Meta:
        model = Post
        fields = ("text", "group", "image")
