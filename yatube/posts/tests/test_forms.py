from http import HTTPStatus

from django.test import Client, TestCase
from django.urls import reverse

from ..models import Group, Post, User


class PostFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.post_author = User.objects.create_user(
            username='post_author',
        )
        cls.group = Group.objects.create(
            title='Тестовое название группы',
            slug='test_slug',
            description='Тестовое описание группы',
        )
        cls.post = Post.objects.create(
            text='Текст поста',
            author=cls.post_author,
            group=cls.group,
        )

        cls.POST_CREATE = reverse('posts:create')
        cls.POST_PROFILE = reverse(
            'posts:profile',
            kwargs={'username': cls.post_author.username}
        )
        cls.POST_EDIT = reverse(
            'posts:edit',
            kwargs={'post_id': cls.post.id}
        )
        cls.POST_DETAIL = reverse(
            'posts:post_detail',
            kwargs={'post_id': cls.post.id}
        )
        cls.LOGIN = reverse('login')

    def setUp(self):
        self.guest_user = Client()
        self.authorized_user = Client()
        self.authorized_user.force_login(self.post_author)

    def test_authorized_user_create_post(self):
        """Проверить создание записи авторизированным клиентом."""
        posts_count = Post.objects.count()
        form_data = {
            'text': 'Текст поста',
            'group': self.group.id,
        }
        response = self.authorized_user.post(
            self.POST_CREATE,
            data=form_data,
            follow=True
        )
        self.assertRedirects(response, self.POST_PROFILE)
        self.assertEqual(Post.objects.count(), posts_count + 1)
        post = Post.objects.first()
        self.assertEqual(post.text, form_data['text'])
        self.assertEqual(post.author, self.post_author)
        self.assertEqual(post.group_id, form_data['group'])

    def test_authorized_user_edit_post(self):
        """Проверить редактирование записи авторизированным клиентом."""
        form_data = {
            'text': 'Отредактированный текст поста',
            'group': self.group.id,
        }
        response = self.authorized_user.post(
            self.POST_EDIT,
            data=form_data,
            follow=True
        )
        self.assertRedirects(response, self.POST_DETAIL)
        post_new = Post.objects.get(id=self.post.id)
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertEqual(post_new.text, form_data['text'])
        self.assertEqual(post_new.author, self.post_author)
        self.assertEqual(post_new.group_id, form_data['group'])

    def test_nonauthorized_user_create_post(self):
        """Проверить создание записи не авторизированным пользователем."""
        posts_count = Post.objects.count()
        form_data = {
            'text': 'Текст поста',
            'group': self.group.id,
        }
        response = self.guest_user.post(
            self.POST_CREATE,
            data=form_data,
            follow=True
        )
        self.assertEqual(response.status_code, HTTPStatus.OK)
        redirect = self.LOGIN + '?next=' + self.POST_CREATE
        self.assertRedirects(response, redirect)
        self.assertEqual(Post.objects.count(), posts_count)
