# Generated by Django 2.1.15 on 2020-09-05 14:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('reservations', '0019_auto_20200816_0920'),
    ]

    operations = [
        migrations.AddField(
            model_name='serviceclass',
            name='level',
            field=models.PositiveIntegerField(default=1),
            preserve_default=False,
        ),
    ]
