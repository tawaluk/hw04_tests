from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from ..models import Comment, Follow, Group, Post

User = get_user_model()


class FollowViewTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(
            username='User1'
        )
        cls.user_2 = User.objects.create_user(
            username='User2'
        )
        cls.follow = Follow.objects.create(
            author=cls.user,
            user=cls.user_2
        )
        cls.group_1 = Group.objects.create(
            title='Цитаты с района',
            slug='test-slug_1',
            description='Многоинтелектуальное описание_1'
        )
        cls.group_2 = Group.objects.create(
            title='Цитаты инстасамки',
            slug='test-slug_2',
            description='Многоинтелектуальное описание_1_2'
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Вся жизнь в трёх строчках',
            group=cls.group_1,
        )
        cls.comment = Comment.objects.create(
            post=cls.post,
            text='Спамный коммент от бота',
            author=cls.user
        )

        cls.PROF_FOLLOW = reverse(
            'posts:profile_follow',
            kwargs={'username': cls.user_2}
        )
        cls.PROF_UNFOLLOW = reverse(
            'posts:profile_unfollow',
            kwargs={'username': cls.user_2}
        )
        cls.FOLLOW_INDEX = reverse('posts:follow_index')

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_follow_another_user(self):
        """Проверить возможность подписки"""
        follow_count = Follow.objects.count()
        self.authorized_client.get(self.PROF_FOLLOW)
        self.assertTrue(
            Follow.objects.filter(
                user=self.user,
                author=self.user_2
            ).exists()
        )
        self.assertEqual(Follow.objects.count(), follow_count + 1)

    def test_unfollow_another_user(self):
        """Проверить возможность отписки"""
        Follow.objects.create(user=self.user, author=self.user_2)
        follow_count = Follow.objects.count()
        self.assertTrue(
            Follow.objects.filter(
                user=self.user,
                author=self.user_2
            ).exists()
        )
        self.authorized_client.get(self.PROF_UNFOLLOW)
        self.assertFalse(
            Follow.objects.filter(
                user=self.user,
                author=self.user_2
            ).exists()
        )
        self.assertEqual(Follow.objects.count(), follow_count - 1)

    def test_new_post_follow(self):
        """Проверить появление новой записи в ленте подписчиков"""
        following = User.objects.create(username='following')
        Follow.objects.create(user=self.user, author=following)
        post = Post.objects.create(author=following, text=self.post.text)
        response = self.authorized_client.get(self.FOLLOW_INDEX)
        self.assertIn(post, response.context['page_obj'].object_list)

    def test_new_post_unfollow(self):
        """Проверить отсутсвие видимости новых записей у неподписчиков"""
        self.client.logout()
        User.objects.create_user(
            username='somobody_temp',
            password='pass'
        )
        self.client.login(username='somobody_temp')
        response = self.authorized_client.get(self.FOLLOW_INDEX)
        self.assertNotIn(
            self.post.text,
            response.context['page_obj'].object_list
        )
