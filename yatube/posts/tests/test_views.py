from django import forms
from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from ..models import Group, Post

User = get_user_model()


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
        for i in range(12):
            Post.objects.create(
                text=f'Текст поста №{i}',
                author=cls.user,
                group=cls.group,
            )
        cls.list_id = Post.objects.all()

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def method_for_tests(self, response, response_second_page):
        sort = Post.objects.all().order_by('-pub_date')
        for i, cont in enumerate(
                response.context['page_obj'].object_list):
            self.assertEqual(cont.text, sort[i].text)
            self.assertEqual(cont.author, sort[i].author)
            self.assertEqual(cont.group, sort[i].group)
        self.assertEqual(len(response.context['page_obj']), 10)
        self.assertEqual(len(response_second_page.context['page_obj']), 2)

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
        self.method_for_tests(response, response_second)

    def test_group_list_current_context(self):
        """Шаблон group_list сформирован с правильным контекстом."""
        response = self.authorized_client.get(
            reverse('posts:group_list', kwargs={'slug': self.group.slug}))
        response_second = self.client.get(
            reverse('posts:group_list',
                    kwargs={'slug': self.group.slug}), {'page': 2})
        self.method_for_tests(response, response_second)

    def test_profile_current_context(self):
        """Шаблон profile сформирован с правильным контекстом."""
        response = self.authorized_client.get(
            reverse('posts:profile', kwargs={'username': self.user}))
        response_second = self.authorized_client.get(
            reverse('posts:profile',
                    kwargs={'username': self.user}), {'page': 2})
        self.method_for_tests(response, response_second)

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
        self.assertEqual(response.context.get(
            'selected_post').group.description, self.group.description)
        self.assertEqual(response.context.get('author'), self.user)
        self.assertEqual(response.context.get('posts_count'), 12)

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
