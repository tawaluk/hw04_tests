from django.test import Client, TestCase
from django.urls import reverse

from ..models import Comment, Post, User


class CommentTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.post_author = User.objects.create(username='comment')
        cls.post = Post.objects.create(
            text='Редактируемый текст',
            author=cls.post_author,
        )
        cls.comment_url = reverse('posts:add_comment', args=['1'])

    def setUp(self):
        self.guest_client = Client()
        self.authorized_user = Client()
        self.authorized_user.force_login(self.post_author)

    def test_authorized_client_comment(self):
        """Проверить возможность комментирования пользователем"""
        text_comment = 'Тестовый комментарий'
        self.authorized_user.post(
            CommentTests.comment_url,
            data={'text': text_comment}
        )
        comment = Comment.objects.filter(post=CommentTests.post).last()
        self.assertEqual(comment.text, text_comment)
        self.assertEqual(comment.post, CommentTests.post)
        self.assertEqual(comment.author, CommentTests.post_author)

    def test_guest_client_comment_redirect_login(self):
        """Проверить возможность комментирования гостем"""
        count_comments = Comment.objects.count()
        self.guest_client.post(CommentTests.comment_url)
        self.assertEqual(count_comments, Comment.objects.count())
