# Generated by Django 2.1.15 on 2020-08-14 02:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('reservations', '0017_salestransaction'),
    ]

    operations = [
        migrations.AddField(
            model_name='reservation_staging',
            name='session_guid',
            field=models.CharField(max_length=100, null=True),
        ),
    ]
