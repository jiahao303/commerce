# Generated by Django 3.2.23 on 2024-06-01 07:56

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('auctions', '0005_listing_created'),
    ]

    operations = [
        migrations.AddField(
            model_name='bid',
            name='user',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='auctions.user'),
            preserve_default=False,
        ),
    ]
