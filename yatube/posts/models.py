from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class Group(models.Model):
    title = models.CharField(
        max_length=200,
        verbose_name='Заголовок',
    )

    slug = models.SlugField(unique=True)

    description = models.TextField(
        max_length=400,
        verbose_name='Описание группы',
        help_text="введите описание группы (максимум 400 символов)"
    )

    def __str__(self):
        return self.title

    class Meta:
        verbose_name_plural = 'Группы'
        verbose_name = 'группы'


class Post(models.Model):
    text = models.TextField(
        verbose_name='Текст поста',
    )

    pub_date = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата публикации',
    )

    author = models.ForeignKey(
        User,
        max_length=30,
        on_delete=models.CASCADE,
        related_name='posts',
        verbose_name='Автор',
    )

    group = models.ForeignKey(
        Group,
        on_delete=models.SET_NULL,
        related_name='posts',
        verbose_name='Принадлежность к группе',
        null=True,
        blank=True,
    )

    def __str__(self):
        return self.text[:100]

    class Meta:
        ordering = ['-pub_date']
        verbose_name_plural = 'Посты'
        verbose_name = 'Пост'
