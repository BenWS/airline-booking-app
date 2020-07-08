# Generated by Django 2.1.15 on 2020-06-24 23:06

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('reservations', '0002_auto_20200618_2144'),
    ]

    operations = [
        migrations.AddField(
            model_name='reservationseat_main',
            name='service_class',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.PROTECT, to='reservations.ServiceClass'),
        ),
        migrations.AddField(
            model_name='reservationseat_staging',
            name='service_class',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.PROTECT, to='reservations.ServiceClass'),
        ),
        migrations.AlterField(
            model_name='passenger_staging',
            name='reservation',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='reservations.Reservation_Staging'),
        ),
    ]
