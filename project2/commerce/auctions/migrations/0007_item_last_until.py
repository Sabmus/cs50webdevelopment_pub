# Generated by Django 4.1.3 on 2022-11-09 15:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('auctions', '0006_item_rename_bid_amount_bid_amount_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='item',
            name='last_until',
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]