import shutil
import tempfile

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from django.urls import reverse

from ..forms import PostForm, CommentForm
from ..models import Group, Post, User, Comment

User = get_user_model()

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
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
        cls.forms = PostForm()

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

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
        """Если форма валидно, то вносятся изменения в пост"""
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

    def test_post_with_image(self):
        """Валидная форма создает запись в Post с изображением"""
        post_count = Post.objects.count()
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
        form_data = {
            'title': 'Заголовок теста картинки',
            'group': self.group.id,
            'text': 'Текст картинки',
            'image': uploaded,
        }
        response = self.authorized_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True
        )
        self.assertRedirects(response, reverse('posts:profile',
                                               kwargs={'username': self.user}))
        self.assertEqual(Post.objects.count(), post_count + 1)
        self.assertTrue(
            Post.objects.filter(
                text=form_data['text'],
                group=self.group.id,
                image='posts/small.gif',
                author=self.user
            ).exists()
        )

    def test_comment_create(self):
        """Валидная форма создаёт комментарий к Посту"""
        comment_count = Comment.objects.count()
        form_data = {
            'text': 'Текст проверки создания коммента'
        }
        response = self.authorized_client.post(
            reverse('posts:add_comment', kwargs={'post_id': self.post.id}),
            data=form_data,
            follow=True
        )
        self.assertRedirects(response, reverse(
            'posts:post_detail', kwargs={'post_id': self.post.id}))
        self.assertEqual(Comment.objects.count(), comment_count + 1)
        self.assertTrue(Comment.objects.filter(
            text='Текст проверки создания коммента',
            author=self.user
        ).exists())

    def test_comment_create_guest(self):
        """Валидная форма не создает коммент в Comment гостем."""
        posts_count = Post.objects.count()
        form_data = {
            'text': 'Какой то текст для проверки коммента'
        }
        response = self.authorized_client.post(
            reverse('posts:add_comment', kwargs={'post_id': self.post.id}),
            data=form_data,
            follow=True
        )
        self.assertRedirects(response, reverse(
            'posts:post_detail', kwargs={'post_id': self.post.id}))
        self.assertEqual(Comment.objects.count(), posts_count)
        self.assertFalse(
            Comment.objects.filter(
                text='Текст проверки создания коммента',
                author=self.user
            ).exists())
