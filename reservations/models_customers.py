import django.utils
from datetime import datetime, timedelta
from django.db import models
from django.contrib.auth.models import User
from .models_planes import Plane,PlaneModel,PlaneSeat, ServiceClass

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
    plane = models.ForeignKey(Plane,on_delete=models.PROTECT, null=True,related_name="+")

class Reservation_Abstract(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name="+")
    departure_flight = models.ForeignKey(Flight, on_delete=models.PROTECT, null=True, related_name="+")
    return_flight = models.ForeignKey(Flight, on_delete=models.PROTECT, null=True, related_name="+")
    number_of_passengers = models.PositiveIntegerField(blank=True)
    created_date = models.DateTimeField(default=django.utils.timezone.now)
    updated_date = models.DateTimeField(default=django.utils.timezone.now)
    round_trip = models.BooleanField(default=False)

    def isvalid(self):
        return django.utils.timezone.now() - timedelta(minutes=15) < self.created_date

    def save(self, *args, **kwargs):
        updated_date = django.utils.timezone.now()
        super().save(*args,**kwargs)

    class Meta:
        abstract = True

class Reservation_Main(Reservation_Abstract):
    pass

class Reservation_Staging(Reservation_Abstract):
    reservation_main = models.ForeignKey(Reservation_Main, null=True, on_delete=models.CASCADE)
    session_guid = models.CharField(max_length=100, null=True)

class ReservationSession(models.Model):
    """
    A ReservationSession object maintains the state of search and selection for flights
    """
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name="+")
    reservation_staging = models.ForeignKey(Reservation_Staging, on_delete=models.PROTECT, null=True, related_name=None)
    departure_airport = models.ForeignKey(Airport, on_delete=models.PROTECT, null=True, related_name="+")
    arrival_airport = models.ForeignKey(Airport, on_delete=models.PROTECT, null=True, related_name="+")
    session_guid = models.CharField(max_length=100, null=False)
    departure_date = models.DateField(auto_now=False, null=True)
    return_date = models.DateField(auto_now=False, null=True)
    number_of_passengers = models.PositiveIntegerField(null=True)
    round_trip = models.CharField(max_length=100, null=True)

class Passenger_Abstract(models.Model):
    departure_flight_seat = models.ForeignKey(PlaneSeat, on_delete=models.CASCADE, null=True, related_name="+")
    return_flight_seat = models.ForeignKey(PlaneSeat, on_delete=models.CASCADE, null=True, related_name="+")
    title = models.CharField(max_length=10, blank=True)
    first_name = models.CharField(max_length=100, blank=True)
    last_name = models.CharField(max_length=100, blank=True)

    class Meta:
        abstract = True

class Passenger_Main(Passenger_Abstract):
    reservation = models.ForeignKey(Reservation_Main, on_delete=models.CASCADE, related_name=None)

class Passenger_Staging(Passenger_Abstract):
    reservation = models.ForeignKey(Reservation_Staging, on_delete=models.CASCADE, related_name=None)

class FlightRetail(models.Model):
    current_retail = models.DecimalField(max_digits=6,decimal_places=2)
    service_class = models.ForeignKey(ServiceClass, on_delete=models.CASCADE,related_name="+")
    flight = models.ForeignKey(Flight,on_delete=models.CASCADE,related_name="+")

class SalesTransaction(models.Model):
    """
    Submitted at customer check
    """
    amount = models.DecimalField(max_digits=6,decimal_places=2)
    reservation = models.ForeignKey(Reservation_Main,on_delete=models.PROTECT)
    passenger = models.ForeignKey(Passenger_Main,on_delete=models.PROTECT)
    flight_type = models.CharField(max_length=100, blank=False)
    log_time = models.DateField(auto_now=True)
