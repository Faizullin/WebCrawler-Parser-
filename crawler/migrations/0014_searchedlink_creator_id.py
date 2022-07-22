# Generated by Django 4.0.4 on 2022-05-16 16:29

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('crawler', '0013_delete_user'),
    ]

    operations = [
        migrations.AddField(
            model_name='searchedlink',
            name='creator_id',
            field=models.ForeignKey(default=0, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
    ]
