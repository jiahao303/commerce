# Generated by Django 3.2.23 on 2024-05-31 18:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('auctions', '0002_bid_comment_listing'),
    ]

    operations = [
        migrations.AlterField(
            model_name='listing',
            name='image',
            field=models.CharField(blank=True, max_length=64, null=True),
        ),
    ]
