# Generated by Django 2.1.15 on 2020-07-25 22:53

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('reservations', '0014_auto_20200711_1408'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='passenger_main',
            name='reservation',
        ),
    ]
