from django.db import models
from django.contrib.auth.models import User
from .models_planes import Plane,PlaneModel,PlaneSeat

class Customer(User):
    pass

class Airport(models.Model):
    airport_code = models.CharField(max_length=10, blank=False)
    airport_name = models.CharField(max_length=100, blank=False)

class Flight(models.Model):
    arrival_airport = models.ForeignKey(Airport, on_delete=models.PROTECT,blank=False)
    departure_airport = models.ForeignKey(Airport, on_delete=models.PROTECT,blank=False)
    departure_datetime = models.DateTimeField(blank=False)
    arrival_datetime = models.DateTimeField(blank=False)

class Reservation(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    # flight = models.ForeignKey(Flight, on_delete=models.CASCADE)
    number_of_passengers = models.PositiveIntegerField(blank=True)
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)
    finalized = models.BooleanField(default=False)
    round_trip = models.BooleanField(default=False)

class Passenger(models.Model):
    reservation = models.ForeignKey(Reservation, on_delete=models.CASCADE)

class ReservationSeat(models.Model):
    flight = models.ForeignKey(Flight, on_delete=models.CASCADE)
    plane_seat = models.ForeignKey(PlaneSeat, on_delete=models.CASCADE)
    reservation = models.ForeignKey(Reservation, on_delete=models.CASCADE)
