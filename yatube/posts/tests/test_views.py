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
        cls.post_page = [Post.objects.create(
            text=f'Тест була №{x}', author=cls.user,
            group=cls.group) for x in range(12)]

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
            reverse('posts:post_detail',
                    kwargs={'post_id': self.post_page[0].id}
                    ): 'posts/post_detail.html',
            reverse('posts:post_create'): 'posts/post_create.html',
            reverse('posts:post_edit', kwargs={'post_id': self.post_page[0].id}
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
            reverse('posts:index'), {'page': 2})
        post_text = ''
        for value in range(len(self.post_page)):
            post_text += self.post_page[value].text
        for cont, i in zip(
                response.context['page_obj'].object_list, range(10)):
            self.assertIn(cont.text, post_text)
            self.assertEqual(cont.author, self.user)
            self.assertEqual(cont.group, self.group)
            self.assertEqual(cont.group.description, self.group.description)
        self.assertEqual(len(response.context['page_obj']), 10)
        self.assertEqual(len(response_second_page.context['page_obj']), 2)

    def test_group_list_current_context(self):
        """Шаблон group_list сформирован с правильным контекстом."""
        response = self.authorized_client.get(
            reverse('posts:group_list', kwargs={'slug': self.group.slug}))
        response_second_page = self.client.get(
            reverse('posts:group_list',
                    kwargs={'slug': self.group.slug}), {'page': 2})
        post_text = ''
        for value in range(len(self.post_page)):
            post_text += self.post_page[value].text
        for cont, i in zip(
                response.context['page_obj'].object_list, range(10)):
            self.assertIn(cont.text, post_text)
            self.assertEqual(cont.author, self.user)
            self.assertEqual(cont.group, self.group)
            self.assertEqual(cont.group.description, self.group.description)
        self.assertEqual(len(response.context['page_obj']), 10)
        self.assertEqual(len(response_second_page.context['page_obj']), 2)

    def test_profile_current_context(self):
        """Шаблон profile сформирован с правильным контекстом."""
        response = self.authorized_client.get(
            reverse('posts:profile', kwargs={'username': self.user}))
        response_second_page = self.authorized_client.get(
            reverse('posts:profile',
                    kwargs={'username': self.user}), {'page': 2})
        post_text = ''
        for value in range(len(self.post_page)):
            post_text += self.post_page[value].text
        for cont, i in zip(
                response.context['page_obj'].object_list, range(10)):
            self.assertIn(cont.text, post_text)
            self.assertEqual(cont.author, self.user)
            self.assertEqual(cont.group, self.group)
            self.assertEqual(cont.group.description, self.group.description)
        self.assertEqual(len(response.context['page_obj']), 10)
        self.assertEqual(len(response_second_page.context['page_obj']), 2)

    def test_post_detail_current_context(self):
        """Шаблон post_detail сформирован с правильным контекстом."""
        response = self.authorized_client.get(
            reverse('posts:post_detail',
                    kwargs={'post_id': self.post_page[0].id}))
        self.assertEqual(response.context.get('selected_post').text,
                         self.post_page[0].text)
        self.assertEqual(response.context.get('selected_post').author,
                         self.user)
        self.assertEqual(response.context.get('selected_post').group,
                         self.post_page[0].group)
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
                    kwargs={'post_id': self.post_page[0].id}))
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
