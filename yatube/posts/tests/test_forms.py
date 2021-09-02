from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from ..models import Group, Post, User

User = get_user_model()


class PostFormTest(TestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.group = Group.objects.create(
            title='Группа для теста',
            slug='Group-Ignat',
            description='Описание'
        )
        cls.user = User.objects.create_user(username='TesterIgnat')
        cls.post = Post.objects.create(
            text='Текст для проверки создания',
            author=cls.user,
            group=cls.group,
        )

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_create_post(self):
        """Валидная форма создает запись в Post."""
        posts_count = Post.objects.count()
        form_data = {
            'text': 'Какой то текст для проверки',
            'group': self.group.id
        }
        response = self.authorized_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True
        )
        self.assertRedirects(response, reverse('posts:profile',
                                               kwargs={'username': self.user}))
        self.assertEqual(Post.objects.count(), posts_count + 1)
        self.assertTrue(
            Post.objects.filter(
                text='Какой то текст для проверки',
                group=self.group.id,
                author=self.user
            ).exists()
        )

    def test_post_edit(self):
        form_data = {
            'text': 'Какой то текст для проверки изменения поста',
            'group': self.group.id
        }
        response = self.authorized_client.post(
            reverse('posts:post_edit', kwargs={'post_id': self.post.id}),
            data=form_data,
            follow=True
        )
        self.assertRedirects(response, reverse(
            'posts:post_detail', kwargs={'post_id': self.post.id}))
        self.assertTrue(
            Post.objects.filter(
                text='Какой то текст для проверки изменения поста',
                group=self.group.id,
                author=self.user
            ).exists()
        )

    def test_create_post_guest(self):
        """Валидная форма не создает запись в Post гостем."""
        posts_count = Post.objects.count()
        form_data = {
            'text': 'Какой то текст для проверки',
            'group': self.group.id
        }
        response = self.guest_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True
        )
        login_url = reverse('users:login')
        new_post_url = reverse('posts:post_create')
        target_url = f'{login_url}?next={new_post_url}'
        self.assertRedirects(response, target_url)
        self.assertEqual(Post.objects.count(), posts_count)
        self.assertFalse(
            Post.objects.filter(
                text='Какой то текст для проверки',
                group=self.group.id,
                author=self.user
            ).exists()
        )
