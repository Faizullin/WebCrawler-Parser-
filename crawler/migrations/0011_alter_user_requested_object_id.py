# Generated by Django 4.0.4 on 2022-05-13 20:31

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('crawler', '0010_user'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='requested_object_id',
            field=models.ForeignKey(default=0, on_delete=django.db.models.deletion.DO_NOTHING, to='crawler.searchedlink'),
        ),
    ]