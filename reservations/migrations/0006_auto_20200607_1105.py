# Generated by Django 2.1.15 on 2020-06-07 15:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('reservations', '0005_auto_20200607_1030'),
    ]

    operations = [
        migrations.AlterField(
            model_name='reservation_staging',
            name='session_guid',
            field=models.CharField(max_length=100),
        ),
    ]
