# Generated by Django 4.1.3 on 2022-11-07 01:57

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('flights', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='flight',
            old_name='destinaton',
            new_name='destination',
        ),
    ]
