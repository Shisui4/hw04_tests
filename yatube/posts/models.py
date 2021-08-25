from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()


class Group(models.Model):
    title = models.CharField("Название группы", max_length=200,
                             help_text='Создайте название группы')
    description = models.TextField("Описание группы")
    slug = models.SlugField(unique=True)

    def __str__(self):
        return self.title


class Post(models.Model):
    text = models.TextField("Текст", help_text='Поле ввода текста')
    pub_date = models.DateTimeField("Дата публикации", auto_now_add=True)
    author = models.ForeignKey(User, verbose_name="Автор",
                               on_delete=models.CASCADE,
                               related_name="posts")
    group = models.ForeignKey(Group, verbose_name="Группа",
                              on_delete=models.SET_NULL,
                              blank=True, null=True, related_name='posts',
                              help_text='Поле выбора группы')

    def __str__(self):
        return self.text
