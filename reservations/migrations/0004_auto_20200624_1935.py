# Generated by Django 2.1.15 on 2020-06-24 23:35

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('reservations', '0003_auto_20200624_1906'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='reservationseat_main',
            name='reservation',
        ),
        migrations.RemoveField(
            model_name='reservationseat_staging',
            name='reservation',
        ),
        migrations.AddField(
            model_name='reservationseat_main',
            name='passenger',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='reservations.Passenger_Main'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='reservationseat_staging',
            name='passenger',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='reservations.Passenger_Staging'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='serviceclass',
            name='name',
            field=models.CharField(max_length=100),
        ),
    ]
