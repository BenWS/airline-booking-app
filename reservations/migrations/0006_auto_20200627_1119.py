# Generated by Django 2.1.15 on 2020-06-27 15:19

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('reservations', '0005_auto_20200627_0807'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='reservationseat_main',
            name='flight',
        ),
        migrations.RemoveField(
            model_name='reservationseat_main',
            name='passenger',
        ),
        migrations.RemoveField(
            model_name='reservationseat_main',
            name='plane_seat',
        ),
        migrations.RemoveField(
            model_name='reservationseat_main',
            name='service_class',
        ),
        migrations.RemoveField(
            model_name='reservationseat_staging',
            name='flight',
        ),
        migrations.RemoveField(
            model_name='reservationseat_staging',
            name='passenger',
        ),
        migrations.RemoveField(
            model_name='reservationseat_staging',
            name='plane_seat',
        ),
        migrations.RemoveField(
            model_name='reservationseat_staging',
            name='service_class',
        ),
        migrations.AddField(
            model_name='passenger_main',
            name='departure_flight_seat',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='+', to='reservations.PlaneSeat'),
        ),
        migrations.AddField(
            model_name='passenger_main',
            name='return_flight_seat',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='+', to='reservations.PlaneSeat'),
        ),
        migrations.AddField(
            model_name='passenger_staging',
            name='departure_flight_seat',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='+', to='reservations.PlaneSeat'),
        ),
        migrations.AddField(
            model_name='passenger_staging',
            name='return_flight_seat',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='+', to='reservations.PlaneSeat'),
        ),
        migrations.DeleteModel(
            name='ReservationSeat_Main',
        ),
        migrations.DeleteModel(
            name='ReservationSeat_Staging',
        ),
    ]
