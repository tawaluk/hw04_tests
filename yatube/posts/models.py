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

    image = models.ImageField(
        verbose_name='Изображение',
        upload_to='posts/',
        blank=True,
    )

    def __str__(self):
        return self.text[:1000]

    class Meta:
        ordering = ['-pub_date']
        verbose_name_plural = 'Посты'
        verbose_name = 'Пост'


class Comment(models.Model):
    post = models.ForeignKey(
        Post,
        related_name='comments',
        verbose_name='Пост',
        on_delete=models.CASCADE,
    )

    author = models.ForeignKey(
        User,
        related_name='comments',
        verbose_name='Автор',
        on_delete=models.CASCADE,
    )

    text = models.TextField(
        verbose_name='Комментарий',
    )

    data_created = models.DateTimeField(
        auto_now=True,
        verbose_name='Дата создания',
    )

    data_updated = models.DateTimeField(
        auto_now=True,
        verbose_name='Дата обновления',
    )

    def __str__(self):
        return self.text[:100]

    class Meta:
        ordering = ['-data_created']
        verbose_name = 'Комментарий'


class Follow(models.Model):
    # пользователь, который подписывается
    user = models.ForeignKey(
        User,
        related_name='follower',
        on_delete=None
    )
    # пользователь, на которого подписывются
    author = models.ForeignKey(
        User,
        related_name='following',
        on_delete=models.CASCADE
    )
