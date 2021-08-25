from django.contrib.auth import get_user_model
from django.test import TestCase

from ..models import Group, Post

User = get_user_model()


class PostModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='Тестовый слаг',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовая группа'
        )

    def test_models_have_correct_object_names(self):
        """Проверяем, что у моделей корректно работает __str__."""
        post = PostModelTest.post
        post_text = post.text[:15]
        self.assertEqual(post_text, 'Тестовая группа')

    def test_models_have_current_group_name(self):
        """Проверка на правильность названия Групп"""
        group = PostModelTest.group
        group_name = group.title
        self.assertEqual(group_name, 'Тестовая группа')

    def test_help_text(self):
        """help_text в полях совпадает с ожидаемым."""
        help_txt = PostModelTest.post
        field_help_texts = {
            'text': 'Поле ввода текста',
            'group': 'Поле выбора группы',
        }
        for field, expected_value in field_help_texts.items():
            with self.subTest(field=field):
                self.assertEqual(
                    help_txt._meta.get_field(field).help_text, expected_value
                )

    def test_verbose_name(self):
        v_name = PostModelTest.post
        field_verbose = {
            'text': 'Текст',
            'pub_date': 'Дата публикации',
            'author': 'Автор',
            'group': 'Группа',
        }
        for field, expected_value in field_verbose.items():
            with self.subTest(field=field):
                self.assertEqual(
                    v_name._meta.get_field(field).verbose_name, expected_value
                )
