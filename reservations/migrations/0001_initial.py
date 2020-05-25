# Generated by Django 2.1.15 on 2020-04-04 20:51

from django.conf import settings
import django.contrib.auth.models
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0009_alter_user_last_name_max_length'),
    ]

    operations = [
        migrations.CreateModel(
            name='Airport',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('airport_code', models.CharField(max_length=10)),
                ('airport_name', models.CharField(max_length=100)),
            ],
        ),
        migrations.CreateModel(
            name='Customer',
            fields=[
                ('user_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'user',
                'verbose_name_plural': 'users',
                'abstract': False,
            },
            bases=('auth.user',),
            managers=[
                ('objects', django.contrib.auth.models.UserManager()),
            ],
        ),
        migrations.CreateModel(
            name='Flight',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('departure_datetime', models.DateTimeField()),
                ('arrival_datetime', models.DateTimeField()),
                ('arrival_airport', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='reservations.Airport')),
                ('departure_airport', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='reservations.Airport')),
            ],
        ),
        migrations.CreateModel(
            name='Passenger',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
            ],
        ),
        migrations.CreateModel(
            name='Plane',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
            ],
        ),
        migrations.CreateModel(
            name='PlaneModel',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
            ],
        ),
        migrations.CreateModel(
            name='PlaneSeat',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('serial_position', models.PositiveIntegerField()),
                ('plane_model', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='reservations.PlaneModel')),
            ],
        ),
        migrations.CreateModel(
            name='Reservation',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('number_of_passengers', models.PositiveIntegerField(blank=True)),
                ('created_date', models.DateTimeField(auto_now_add=True)),
                ('updated_date', models.DateTimeField(auto_now=True)),
                ('finalized', models.BooleanField(default=False)),
                ('customer', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='reservations.Customer')),
            ],
        ),
        migrations.CreateModel(
            name='ReservationSeat',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('flight', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='reservations.Flight')),
                ('plane_seat', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='reservations.PlaneSeat')),
            ],
        ),
        migrations.AddField(
            model_name='plane',
            name='plane_model',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='reservations.PlaneModel'),
        ),
        migrations.AddField(
            model_name='passenger',
            name='reservation',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='reservations.Reservation'),
        ),
    ]
