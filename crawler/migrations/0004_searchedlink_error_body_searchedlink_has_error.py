# Generated by Django 4.0.4 on 2022-05-13 15:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('crawler', '0003_remove_searchedlink_error_body_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='searchedlink',
            name='error_body',
            field=models.CharField(default='no', max_length=50, verbose_name='Ошибка'),
        ),
        migrations.AddField(
            model_name='searchedlink',
            name='has_error',
            field=models.BooleanField(default=False, verbose_name='Наличие ошибки'),
        ),
    ]
