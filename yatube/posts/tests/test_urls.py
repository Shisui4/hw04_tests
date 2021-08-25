from django.contrib.auth import get_user_model
from django.test import Client, TestCase

from ..models import Group, Post

User = get_user_model()


class StaticURLTests(TestCase):

    def setUp(self):
        self.guest_client = Client()

    def test_homepage(self):
        response = self.guest_client.get('/')
        self.assertEqual(response.status_code, 200)

    def test_author(self):
        response = self.guest_client.get('/about/author/')
        self.assertEqual(response.status_code, 200)

    def test_tech(self):
        response = self.guest_client.get('/about/tech/')
        self.assertEqual(response.status_code, 200)


class PostURLTests(TestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.group = Group.objects.create(
            title='Группа тестовая',
            slug='test-slug'
        )
        cls.user = User.objects.create_user(username='author')
        cls.post = Post.objects.create(
            text='Какой то текст',
            author=cls.user,
            group=cls.group
        )
        cls.authorized_client = Client()
        cls.authorized_client.force_login(cls.user)
        cls.guest_client = Client()

    def test_urls_current_use_template(self):
        """Проверка использования шаблонов для страниц"""
        templates_urls_use = {
            'posts/index.html': '/',
            'posts/group_list.html': '/group/test-slug/',
            'posts/profile.html': '/profile/author/',
            'posts/post_detail.html': '/posts/1/',
            'posts/post_create.html': '/create/',
            'posts/post_create.html': '/posts/1/edit/'
        }
        for template, adress in templates_urls_use.items():
            with self.subTest(adress=adress):
                response = self.authorized_client.get(adress)
                self.assertTemplateUsed(response, template)

    def test_availability_check_all(self):
        """Проверка доступности стр. неавтор-му польз-ю"""
        list_html_status = {
            '/': 200,
            '/group/test-slug/': 200,
            '/profile/author/': 200,
            '/posts/1/': 200,
        }
        for adress, status_code in list_html_status.items():
            with self.subTest(status_code=status_code):
                response = self.guest_client.get(adress)
                self.assertEqual(response.status_code, status_code)

    def test_availability_check_404(self):
        """Проверка доступности стр. неавтор-му польз-ю"""
        adress_404 = '/unexisting_page/'
        response = self.guest_client.get(adress_404)
        self.assertEqual(response.status_code, 404)

    def test_availability_check_authorized(self):
        """Проверка доступности стр. создания поста юзеру"""
        adress_create = '/create/'
        response = self.authorized_client.get(adress_create)
        self.assertEqual(response.status_code, 200)

    def test_availability_check_author(self):
        """Проверка доступности стр. изменения поста автором"""
        adress_edit = '/posts/1/edit/'
        response = self.authorized_client.get(adress_edit)
        self.assertEqual(response.status_code, 200)
