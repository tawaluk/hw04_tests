from django.core.cache import cache
from django.test import TestCase
from django.urls import reverse

from ..models import Post, User


class CacheTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.test_user = User.objects.create(username='cache')
        cls.post = Post.objects.create(
            text='Тесты = скука!',
            author=cls.test_user,
        )

        cls.INDEX = reverse('posts:index')

    def test_pages_uses_correct_template(self):
        """Проверить кэш постов на корневой странице"""
        response = self.client.get(self.INDEX)
        cached_response_content = response.content
        Post.objects.create(text='Второй пост', author=self.test_user)
        response = self.client.get(self.INDEX)
        self.assertEqual(cached_response_content, response.content)
        cache.clear()
        response = self.client.get(self.INDEX)
        self.assertNotEqual(cached_response_content, response.content)
