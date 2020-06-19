from django.db import models
from django.contrib.auth.models import User
from .models_planes import Plane,PlaneModel,PlaneSeat



class Customer(User):
    pass

class Airport(models.Model):
    airport_code = models.CharField(max_length=10, blank=False)
    airport_name = models.CharField(max_length=100, blank=False)

class Flight(models.Model):
    arrival_airport = models.ForeignKey(Airport, on_delete=models.PROTECT,blank=False, related_name = "+")
    departure_airport = models.ForeignKey(Airport, on_delete=models.PROTECT,blank=False, related_name = "+")
    departure_datetime = models.DateTimeField(blank=False)
    arrival_datetime = models.DateTimeField(blank=False)

class Reservation_Abstract(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name="+")
    departure_flight = models.ForeignKey(Flight, on_delete=models.PROTECT, null=True, related_name="+")
    return_flight = models.ForeignKey(Flight, on_delete=models.PROTECT, null=True, related_name="+")
    number_of_passengers = models.PositiveIntegerField(blank=True)
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)
    round_trip = models.BooleanField(default=False)

    class Meta:
        abstract = True

class Reservation_Main(Reservation_Abstract):
    pass

class Reservation_Staging(Reservation_Abstract):
    reservation_main = models.ForeignKey(Reservation_Main, null=True, on_delete=models.CASCADE)

class Passenger_Abstract(models.Model):
    reservation = models.ForeignKey(Reservation_Main, on_delete=models.CASCADE)
    title = models.CharField(max_length=10, blank=True)
    first_name = models.CharField(max_length=100, blank=True)
    last_name = models.CharField(max_length=100, blank=True)

    class Meta:
        abstract = True

class Passenger_Main(Passenger_Abstract):
    pass

class Passenger_Staging(Passenger_Abstract):
    pass

class ReservationSeat_Abstract(models.Model):
    flight = models.ForeignKey(Flight, on_delete=models.CASCADE)
    plane_seat = models.ForeignKey(PlaneSeat, on_delete=models.CASCADE)
    reservation = models.ForeignKey(Reservation_Main, on_delete=models.CASCADE)

    class Meta:
        abstract = True

class ReservationSeat_Main(ReservationSeat_Abstract):
    pass

class ReservationSeat_Staging(ReservationSeat_Abstract):
    pass

class ReservationSession(models.Model):
    session_guid = models.CharField(max_length=100, null=False)
    reservation_staging = models.ForeignKey(Reservation_Staging, on_delete=models.PROTECT, null=True, related_name = "+")
    departure_airport = models.ForeignKey(Airport, on_delete=models.PROTECT, null=True, related_name="+")
    arrival_airport = models.ForeignKey(Airport, on_delete=models.PROTECT, null=True, related_name="+")
    departure_date = models.DateField(auto_now=False)
    return_date = models.DateField(auto_now=False)
    number_of_passengers = models.PositiveIntegerField(blank=True)
    round_trip = models.CharField(max_length=100, null=True)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name="+")

class ServiceClass(models.Model):
    name = models.CharField(max_length=10)