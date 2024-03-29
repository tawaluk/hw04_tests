from django import forms

from django.test import Client, TestCase
from django.urls import reverse
from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile


from ..models import Group, Post, User


class PostPagesTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Тестовое описание группы',
        )

        small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        uploaded = SimpleUploadedFile(
            name='small.gif',
            content=small_gif,
            content_type='image/gif'
        )

        cls.post = Post.objects.create(
            text='Тестовый текст поста',
            author=cls.user,
            group=cls.group,
            image=uploaded,
        )

        cls.ROOT_REVERSE = reverse('posts:index')
        cls.CRATE_REVERSE = reverse('posts:create')
        cls.GROUP_REVERSE = reverse(
            'posts:group_posts',
            kwargs={'slug': cls.group.slug})
        cls.PROFILE_REVERSE = reverse(
            'posts:profile',
            kwargs={'username': cls.user.username})
        cls.POST_DETAIL_REVERSE = reverse(
            'posts:post_detail',
            kwargs={'post_id': cls.post.id})
        cls.EDIT_REVERSE = reverse(
            'posts:edit',
            kwargs={'post_id': cls.post.id, })

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def check_post_info(self, post):
        self.assertEqual(post.text, self.post.text)
        self.assertEqual(post.author, self.post.author)
        self.assertEqual(post.group.id, self.post.group.id)
        self.assertEqual(post.image, self.post.image)

    def test_forms_show_correct(self):
        """Проверка коректности формы."""
        context = {
            self.CRATE_REVERSE,
            self.EDIT_REVERSE,
        }
        for reverse_page in context:
            with self.subTest(reverse_page=reverse_page):
                response = self.authorized_client.get(reverse_page)
                self.assertIsInstance(
                    response.context['form'].fields['text'],
                    forms.fields.CharField)
                self.assertIsInstance(
                    response.context['form'].fields['group'],
                    forms.fields.ChoiceField)
                self.assertIsInstance(
                    response.context['form'].fields['image'],
                    forms.fields.ImageField)

    def test_index_page_show_correct_context(self):
        """Шаблон index.html сформирован с правильным контекстом."""
        response = self.authorized_client.get(self.ROOT_REVERSE)
        self.check_post_info(response.context['page_obj'][0])

    def test_groups_page_show_correct_context(self):
        """Шаблон group_list.html сформирован с правильным контекстом."""
        response = self.authorized_client.get(self.GROUP_REVERSE)
        self.assertEqual(response.context['group'], self.group)
        self.check_post_info(response.context['page_obj'][0])

    def test_profile_page_show_correct_context(self):
        """Шаблон profile.html сформирован с правильным контекстом."""
        response = self.authorized_client.get(self.PROFILE_REVERSE)
        self.assertEqual(response.context['author'], self.user)
        self.check_post_info(response.context['page_obj'][0])

    def test_detail_page_show_correct_context(self):
        """Шаблон post_detail.html сформирован с правильным контекстом."""
        response = self.authorized_client.get(self.POST_DETAIL_REVERSE)
        self.check_post_info(response.context['post'])


class PaginatorTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        list_of_posts: Post = []

        cls.guest_client = Client()

        cls.user = User.objects.create(username='HasNoName')
        cls.authorized_client = Client()
        cls.authorized_client.force_login(cls.user)

        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='some-slug',
            description='Тестовое описание',
        )

        for _ in range(settings.NUMBER_OF_TEST_POSTS):
            list_of_posts.append(
                Post(
                    text='Один из многих',
                    author=cls.user,
                    group=cls.group,
                )
            )

        Post.objects.bulk_create(list_of_posts)

    def test_paginator_on_three_pages(self):
        """Проверка работы паджинатора."""
        group_page = '/group/some-slug/'
        profile_page = '/profile/HasNoName/'
        index_page = '/'

        NUM_LOST_PAGES = (
            settings.NUMBER_OF_TEST_POSTS // settings.NUM_OF_POSTS
        ) + 1  # Номер последней страницы

        lost_page = f'?page={NUM_LOST_PAGES}'

        POSTS_LOST = settings.NUMBER_OF_TEST_POSTS % settings.NUM_OF_POSTS

        page_expected_posts = {
            group_page: settings.NUM_OF_POSTS,
            profile_page: settings.NUM_OF_POSTS,
            index_page: settings.NUM_OF_POSTS,
            group_page + lost_page: POSTS_LOST,
            profile_page + lost_page: POSTS_LOST,
            index_page + lost_page: POSTS_LOST
        }

        for page, expected_number_of_posts in page_expected_posts.items():
            with self.subTest(page=page):
                response = self.guest_client.get(page)
                total_posts_on_page = len(response.context['page_obj'])

                self.assertEqual(
                    total_posts_on_page,
                    expected_number_of_posts
                )
