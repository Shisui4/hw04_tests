import shutil
import tempfile
from datetime import timedelta

from django import forms
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from django.urls import reverse

from ..models import Group, Post

User = get_user_model()
TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostsPageTest(TestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.group = Group.objects.create(
            title='Группа для теста',
            slug='Group-Ignat',
            description='Описание'
        )
        cls.group_more = Group.objects.create(
            title='Группа для теста группы',
            slug='Group-Stoner',
            description='Stoner'
        )
        cls.user = User.objects.create_user(username='TesterIgnat')
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
        cls.post_page = Post.objects.bulk_create([
            Post(text='Тест булка 1', author=cls.user, group=cls.group,
                 image=uploaded),
            Post(text='Тест булки 2', author=cls.user, group=cls.group,
                 image=uploaded),
            Post(text='Тест балки 3', author=cls.user, group=cls.group,
                 image=uploaded),
            Post(text='Тест булки 4', author=cls.user, group=cls.group,
                 image=uploaded),
            Post(text='Тест балки 5', author=cls.user, group=cls.group,
                 image=uploaded),
            Post(text='Тест булка 6', author=cls.user, group=cls.group,
                 image=uploaded),
            Post(text='Тест булки 7', author=cls.user, group=cls.group,
                 image=uploaded),
            Post(text='Тест балки 8', author=cls.user, group=cls.group,
                 image=uploaded),
            Post(text='Тест булка 9', author=cls.user, group=cls.group,
                 image=uploaded),
            Post(text='Тест балки 10', author=cls.user, group=cls.group,
                 image=uploaded),
            Post(text='Тест бул 11', author=cls.user, group=cls.group,
                 image=uploaded),
            Post(text='Тест бал 12', author=cls.user, group=cls.group,
                 image=uploaded),
            Post(text='Тест с картинкой', author=cls.user, group=cls.group,
                 image=uploaded)
        ])
        cls.list_id = Post.objects.all()

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        time_update = []
        for i, post in enumerate(Post.objects.all()):
            self.post_page[i].pub_date += timedelta(hours=i)
            time_update.append(post)
        Post.objects.bulk_update(time_update, ['pub_date'])

    def comparing_posts_in_context(self, response, response_second_page):
        sort = Post.objects.all().order_by('-pub_date')
        for i, cont in enumerate(
                response.context['page_obj'].object_list):
            self.assertEqual(cont.text, sort[i].text)
            self.assertEqual(cont.author, sort[i].author)
            self.assertEqual(cont.group, sort[i].group)
            self.assertEqual(cont.image, sort[i].image)
        self.assertEqual(len(response.context['page_obj']), 10)
        self.assertEqual(len(response_second_page.context['page_obj']), 3)

    def test_pages_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        templates_pages_name = {
            reverse('posts:index'): 'posts/index.html',
            reverse('posts:group_list',
                    kwargs={'slug': self.group.slug}): 'posts/group_list.html',
            reverse('posts:profile',
                    kwargs={'username': self.user}): 'posts/profile.html',
            reverse('posts:post_detail',
                    kwargs={'post_id': self.list_id[0].id}
                    ): 'posts/post_detail.html',
            reverse('posts:post_create'): 'posts/post_create.html',
            reverse('posts:post_edit', kwargs={'post_id': self.list_id[0].id}
                    ): 'posts/post_create.html',
        }
        for reverse_name, template in templates_pages_name.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_index_current_context(self):
        """Шаблон index сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse('posts:index'))
        response_second = self.client.get(
            reverse('posts:index'), {'page': 2})
        self.comparing_posts_in_context(response, response_second)

    def test_group_list_current_context(self):
        """Шаблон group_list сформирован с правильным контекстом."""
        response = self.authorized_client.get(
            reverse('posts:group_list', kwargs={'slug': self.group.slug}))
        response_second = self.client.get(
            reverse('posts:group_list',
                    kwargs={'slug': self.group.slug}), {'page': 2})
        self.comparing_posts_in_context(response, response_second)

    def test_profile_current_context(self):
        """Шаблон profile сформирован с правильным контекстом."""
        response = self.authorized_client.get(
            reverse('posts:profile', kwargs={'username': self.user}))
        response_second = self.authorized_client.get(
            reverse('posts:profile',
                    kwargs={'username': self.user}), {'page': 2})
        self.comparing_posts_in_context(response, response_second)

    def test_post_detail_current_context(self):
        """Шаблон post_detail сформирован с правильным контекстом."""
        response = self.authorized_client.get(
            reverse('posts:post_detail',
                    kwargs={'post_id': self.list_id[0].id}))
        self.assertEqual(response.context.get('selected_post').text,
                         self.list_id[0].text)
        self.assertEqual(response.context.get('selected_post').author,
                         self.user)
        self.assertEqual(response.context.get('selected_post').group,
                         self.list_id[0].group)
        self.assertEqual(response.context.get('selected_post').image,
                         self.list_id[0].image)
        self.assertEqual(response.context.get(
            'selected_post').group.description, self.group.description)
        self.assertEqual(response.context.get('author'), self.user)
        self.assertEqual(response.context.get('posts_count'), 13)

    def test_post_create_current_context(self):
        """Шаблон post_create сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse('posts:post_create'))
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)

    def test_post_edit_current_context(self):
        """Шаблон post_edit сформирован с правильным контекстом."""
        response = self.authorized_client.get(
            reverse('posts:post_edit',
                    kwargs={'post_id': self.list_id[0].id}))
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)

    def test_post_not_in_another_group(self):
        """Пост с группой group не добавился в group_more"""
        response = self.authorized_client.get(
            reverse('posts:group_list', kwargs={'slug': self.group_more.slug}))
        self.assertEqual(len(response.context['page_obj']), 0)

    def test_page_with_image(self):
        response = self.authorized_client.get(reverse('posts:index'))
        sort = Post.objects.all().order_by('-pub_date')
        post = response.context['page_obj'].object_list[0]
        self.assertEqual(post.image, sort[0].image)
