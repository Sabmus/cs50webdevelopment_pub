# Generated by Django 4.1.3 on 2022-11-23 22:08

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('network', '0006_post_liked_by'),
    ]

    operations = [
        migrations.RenameField(
            model_name='post',
            old_name='like',
            new_name='like_count',
        ),
    ]