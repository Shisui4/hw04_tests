import time

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
        cls.user = User.objects.create_user(username='TesterIgnat')
        cls.post_page = Post.objects.bulk_create([
            Post(text='Тест булка 1', author=cls.user, group=cls.group, pk=1),
            Post(text='Тест булки 2', author=cls.user, group=None, pk=2),
            Post(text='Тест балки 3', author=cls.user, group=None, pk=3),
            Post(text='Тест булки 4', author=cls.user, group=None, pk=4),
            Post(text='Тест балки 5', author=cls.user, group=None, pk=5),
            Post(text='Тест булка 6', author=cls.user, group=None, pk=6),
            Post(text='Тест булки 7', author=cls.user, group=None, pk=7),
            Post(text='Тест балки 8', author=cls.user, group=cls.group, pk=8),
            Post(text='Тест булка 9', author=cls.user, group=None, pk=9),
            Post(text='Тест балки 10', author=cls.user, group=None, pk=10),
            Post(text='Тест бул 11', author=cls.user, group=cls.group, pk=11),
            Post(text='Тест бал 12', author=cls.user, group=cls.group, pk=12),
        ])
        time.sleep(0.001)
        cls.post = Post.objects.create(
            text='Тест созданной записи',
            author=cls.user,
            group=cls.group,
            id=13
        )

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_pages_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        templates_pages_name = {
            reverse('posts:index'): 'posts/index.html',
            reverse('posts:group_list',
                    kwargs={'slug': self.group.slug}): 'posts/group_list.html',
            reverse('posts:profile',
                    kwargs={'username': self.user}): 'posts/profile.html',
            reverse('posts:post_detail', kwargs={'post_id': self.post.id}
                    ): 'posts/post_detail.html',
            reverse('posts:post_create'): 'posts/post_create.html',
            reverse('posts:post_edit', kwargs={'post_id': self.post.id}
                    ): 'posts/post_create.html',
        }
        for reverse_name, template in templates_pages_name.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_index_current_context(self):
        """Шаблон index сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse('posts:index'))
        response_second_page = self.client.get(
            reverse('posts:index') + '?page=2')
        first_object = response.context['page_obj'][0]
        index_text_0 = first_object.text
        index_author_0 = first_object.author
        index_group_0 = first_object.group
        index_group_description_0 = first_object.group.description
        self.assertEqual(index_text_0, self.post.text)
        self.assertEqual(index_author_0, self.user)
        self.assertEqual(index_group_0, self.group)
        self.assertEqual(index_group_description_0, self.group.description)
        self.assertEqual(len(response.context['page_obj']), 10)
        self.assertEqual(len(response_second_page.context['page_obj']), 3)
        print()

    def test_group_list_current_context(self):
        """Шаблон group_list сформирован с правильным контекстом."""
        response = self.authorized_client.get(
            reverse('posts:group_list', kwargs={'slug': self.group.slug}))
        first_object = response.context['page_obj'][0]
        index_text_0 = first_object.text
        index_author_0 = first_object.author
        index_group_0 = first_object.group
        index_group_description_0 = first_object.group.description
        self.assertEqual(index_text_0, self.post.text)
        self.assertEqual(index_author_0, self.user)
        self.assertEqual(index_group_0, self.group)
        self.assertEqual(index_group_description_0, self.group.description)
        self.assertEqual(len(response.context['page_obj']), 5)

    def test_profile_current_context(self):
        """Шаблон profile сформирован с правильным контекстом."""
        response = self.authorized_client.get(
            reverse('posts:profile', kwargs={'username': self.user}))
        response_second_page = self.authorized_client.get(
            reverse('posts:profile',
                    kwargs={'username': self.user}) + '?page=2')
        first_object = response.context['page_obj'][0]
        index_text_0 = first_object.text
        index_author_0 = first_object.author
        index_group_0 = first_object.group
        index_group_description_0 = first_object.group.description
        self.assertEqual(index_text_0, self.post.text)
        self.assertEqual(index_author_0, self.user)
        self.assertEqual(index_group_0, self.group)
        self.assertEqual(index_group_description_0, self.group.description)
        self.assertEqual(len(response.context['page_obj']), 10)
        self.assertEqual(len(response_second_page.context['page_obj']), 3)

    def test_post_detail_current_context(self):
        """Шаблон post_detail сформирован с правильным контекстом."""
        response = self.authorized_client.get(
            reverse('posts:post_detail',
                    kwargs={'post_id': self.post.id}))
        self.assertEqual(response.context.get('selected_post').text,
                         self.post.text)
        self.assertEqual(response.context.get('selected_post').author,
                         self.user)
        self.assertEqual(response.context.get('selected_post').group,
                         self.post.group)
        self.assertEqual(response.context.get(
            'selected_post').group.description, self.group.description)
        self.assertEqual(response.context.get('author'), self.user)
        self.assertEqual(response.context.get('posts_count'), 13)
        print(response.context.get('posts_count'))

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
            reverse('posts:post_edit', kwargs={'post_id': self.post.id}))
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)

    def test_static_page_accessible_by_name(self):
        """URL, генерируемый при помощи имени static_pages, доступен."""
        template_name = {
            'about:author': 200,
            'about:tech': 200,
        }
        for address, status_code in template_name.items():
            with self.subTest(status_code=status_code):
                response = self.authorized_client.get(reverse(address))
                self.assertEqual(response.status_code, status_code)

    def test_static_page_correct_template(self):
        """При запросе к staticpages
                применяется шаблон staticpages/"""
        template_name = {
            'about:author': 'about/author.html',
            'about:tech': 'about/tech.html',
        }
        for address, template in template_name.items():
            with self.subTest(template=template):
                response = self.authorized_client.get(reverse(address))
                self.assertTemplateUsed(response, template)
