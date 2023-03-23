from django import forms

from .models import Comment, Post


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ['text', 'group', 'image']
        help_texts = {
            'text': 'Текст нового поста',
            'group': 'Группа, к которой будет относится пост',
            'image': 'выбрать картинку',
        }


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['text']
        help_text = {
            'text': 'Текст поста'
        }