from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.test import Client, TestCase
from django.urls import reverse

from ..models import Group, Post

User = get_user_model()


class CacheWorkTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='tester-Ignat')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test_slug',
            description='test description'
        )
        cls.post = Post.objects.create(
            text='Тестовый текст',
            author=cls.user,
            group=cls.group,
        )
        cache.clear()

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        cache.clear()

    def test_index_page_cached(self):
        """Проверка работы кэша на главной странице"""
        response = self.authorized_client.get(reverse('posts:index'))
        first = response.content
        self.post.delete()

        response_check = self.authorized_client.get(reverse('posts:index'))
        self.assertEqual(first, response_check.content)

        cache.clear()
        response_second = self.authorized_client.get(reverse('posts:index'))
        self.assertNotEqual(first, response_second.content)
