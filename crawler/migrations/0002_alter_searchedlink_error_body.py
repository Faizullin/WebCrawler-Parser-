# Generated by Django 4.0.4 on 2022-05-13 15:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('crawler', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='searchedlink',
            name='error_body',
            field=models.CharField(default='', max_length=50, verbose_name='Ошибка'),
        ),
    ]