# Generated by Django 2.2.16 on 2021-09-04 10:33

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('posts', '0009_auto_20210904_2032'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='group',
            options={'ordering': ('title',), 'verbose_name': 'Группа', 'verbose_name_plural': 'Группы'},
        ),
    ]
