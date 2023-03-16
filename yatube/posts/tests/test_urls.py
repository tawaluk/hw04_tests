from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import TestCase, Client

from posts.models import Group, Post

User = get_user_model()


class PostURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.guest_client = Client()
        cls.user = User.objects.create(username='HasNoName')
        cls.authorized_user = Client()
        cls.authorized_user.force_login(cls.user)

        cls.user_not_author = User.objects.create(username='NotAuthor')
        cls.authorized_not_author_client = Client()
        cls.authorized_not_author_client.force_login(cls.user_not_author)

        cls.post = Post.objects.create(
            text='Тестовый пост',
            author=cls.user,
        )
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='some-slug',
            description='Тестовое описание',
        )

    def test_home_url_all(self):
        """Проверить доступность главной страницы, для всех пользователей"""
        response = self.guest_client.get('/')
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_group_url(self):
        """Проверить доступность групповой страницы, для всех пользователей"""
        response = self.guest_client.get('/group/some-slug/')
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_profile_url(self):
        """Проверить доступность страницы профиля, для всех пользователей"""
        response = self.guest_client.get('/profile/HasNoName/')
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_post_url(self):
        """Проверить доступность страницы поста, для всех пользователей"""
        response = self.guest_client.get(f'/posts/{self.post.id}/')
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_post_edit_url_author(self):
        """
        Проверить доступность страницы редактирования поста,
         только для автора
        """
        response_author = self.authorized_user.get(
            f'/posts/{self.post.id}/edit/'
        )
        self.assertEqual(
            response_author.status_code, HTTPStatus.OK
        )

    def test_post_edit_url_all(self):
        """
        Проверить доступность страницы редактирования поста,
         только для гостей
        """
        response_all = self.guest_client.get(
            f'/posts/{self.post.id}/edit/'
        )
        self.assertEqual(
            response_all.status_code, HTTPStatus.FOUND
        )

    def test_post_edit_not_author(self):
        """
        Проверить доступность страницы редактирования поста,
         для пользователей сайта (не авторы)
        """
        response_not_author = self.authorized_not_author_client.get(
            f'/posts/{self.post.id}/edit/'
        )
        self.assertEqual(
            response_not_author.status_code, HTTPStatus.FOUND
        )

    def test_post_create_url(self):
        """
        Проверить доступность страницы создания поста,
         только для пользователей сайта
        """
        response_authorized = self.authorized_user.get('/create/')
        response_not_author = self.guest_client.get('/create/')

        self.assertEqual(response_authorized.status_code, HTTPStatus.OK)
        self.assertEqual(
            response_not_author.status_code,
            HTTPStatus.FOUND
        )

    def test_404_url_all(self):
        """
        Проверить доступность несуществующей страницы,
         для всех
        """
        response = self.guest_client.get('/perpetual motion machine/')

        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)

    def test_urls_uses_correct_template(self):
        """Проверить название шаблонов."""
        templates_url_names = {
            '/group/some-slug/': 'posts/group_list.html',
            '/profile/HasNoName/': 'posts/profile.html',
            f'/posts/{self.post.id}/': 'posts/post_detail.html',
            '/create/': 'posts/create_post.html',
            f'/posts/{self.post.id}/edit/': 'posts/create_post.html',
            '/': 'posts/index.html',
        }
        for address, template in templates_url_names.items():
            with self.subTest(address=address):
                response = self.authorized_user.get(address)
                self.assertTemplateUsed(response, template)
