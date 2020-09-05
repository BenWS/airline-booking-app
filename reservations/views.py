from django.shortcuts import HttpResponse, render, reverse, HttpResponseRedirect
from django.db.models import Q, Window, F
from django.db.models.functions import DenseRank
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.template import loader

import json
import uuid
from datetime import date

from prompt_toolkit import prompt

from .models_customers import *
from .views_development import *


def as_currency(amount):
    if amount >= 0:
        return '${:,.2f}'.format(amount)
    else:
        return '-${:,.2f}'.format(-amount)

def iif(condition, value_if_true, value_if_false):
    if condition:
        return value_if_true
    elif not condition:
        return value_if_false

def getAvailableFlightSeats(flight_id):
    pass


def test(request):
    return HttpResponse(test_logic())

# Create your views here.
def index(request):
    return render(request, "reservations/index.html")


def userCreation(request):
    if request.method == "GET":
        return render(request, "reservations/create-account.html")
    if request.method == "POST":
        customer = Customer.objects.create_user(
            username=request.POST['username'],
            email=request.POST['email_address'],
            password=request.POST['password'],
            first_name=request.POST['first_name'],
            last_name=request.POST['last_name']
        )
        login(request, customer)
        return HttpResponseRedirect(reverse('reservations:index'))


def userSignIn(request):
    if request.method == "GET":
        return render(request, "reservations/sign-in.html")
    if request.method == "POST":
        customer = authenticate(
            request
            , username=request.POST['username']
            , password=request.POST['password']
        )
        login(request, customer)
        return HttpResponseRedirect(reverse('reservations:index'))

def userSignOut(request):
    logout(request)
    return HttpResponseRedirect(reverse('reservations:index'))


def bookReservation(request):
    if request.method == "GET":
        return render(request, "reservations/book.html")

def getMyTrips(request):
    # get user's reservations
    reservations = Reservation_Main.objects.filter(customer=request.user)
    print(reservations)

    # get flight #s of user's reservations

    context = {
       "reservations":[
           {
               "reservation_id":reservation.id,
               "departure_flight_id": reservation.departure_flight.id,
               "return_flight_id": reservation.return_flight.id,
               "departure_flight_datetime": reservation.departure_flight.departure_datetime,
               "departure_flight_plane_make": reservation.departure_flight.plane.plane_model.make_name,
               "departure_flight_plane_model": reservation.departure_flight.plane.plane_model.model_name,
               "return_flight_datetime": reservation.return_flight.departure_datetime,
               "return_flight_plane_make": reservation.return_flight.plane.plane_model.make_name,
               "return_flight_plane_model": reservation.return_flight.plane.plane_model.model_name,
               "departflight_departure_airport": reservation.departure_flight.departure_airport.airport_code,
               "departflight_arrival_airport": reservation.departure_flight.arrival_airport.airport_code,
               "returnflight_departure_airport": reservation.return_flight.departure_airport.airport_code,
               "returnflight_arrival_airport": reservation.return_flight.arrival_airport.airport_code
           }
           for reservation in reservations
        ]
    }

    if request.user.is_authenticated:
        # template = loader.get_template('reservations/my-trips/my-trips.html')
        return render(request,'reservations/my-trips/my-trips.html',context=context)

    else:
        return HttpResponse(reverse('reservations:sign-in'))

def myTrips_getFlightStatus(request):
    return render(request,'reservations/my-trips/flight-status.html')

def myTrips_getView(request):
    reservation_main = Reservation_Main.objects.get(id=request.GET['reservation_id'])
    return_flight = reservation_main.return_flight
    departure_flight = reservation_main.departure_flight

    # departure flight context
    # departure passengers linked to reservation
    queryresult_departurepassenger = Passenger_Main.objects \
        .filter(reservation_id=reservation_main.id, departure_flight_seat__isnull=False) \
        .annotate(assignment_number=Window(DenseRank(), partition_by=[F('reservation')], order_by=F('id').asc()))

    departure_flight_detail = [
        {
            "passenger_id": passenger.id,
            "assignment_number": passenger.assignment_number,
            "service_class": passenger.departure_flight_seat.service_class.name,
            "cabin_position": passenger.departure_flight_seat.cabin_position,
            "current_retail": FlightRetail.objects.get(
                Q(flight=passenger.reservation.departure_flight)
                & Q(service_class=passenger.departure_flight_seat.service_class)).current_retail
        }
        for passenger in queryresult_departurepassenger
    ]

    # get flight retail for each passenger associated with reservation departure flight
    total_cost_flight = sum([
        FlightRetail.objects.get(
            Q(flight=departure_flight)
            & Q(service_class=passenger.departure_flight_seat.service_class)).current_retail

        for passenger in queryresult_departurepassenger
    ])

    departure_flight_summary = {
        "flight_id": reservation_main.departure_flight.id,
        "plane_model": reservation_main.return_flight.plane.plane_model.model_name,
        "plane_make": reservation_main.return_flight.plane.plane_model.make_name,
        "departure_datetime": reservation_main.departure_flight.departure_datetime,
        "arrival_datetime": reservation_main.departure_flight.arrival_datetime,
        "number_of_passengers": queryresult_departurepassenger.count(),
        "total_cost_flight": total_cost_flight
    }

    # return flight context
    queryresult_returnpassenger = Passenger_Main.objects \
        .filter(reservation_id=reservation_main.id, return_flight_seat__isnull=False) \
        .annotate(assignment_number=Window(DenseRank(), partition_by=[F('reservation')], order_by=F('id').asc()))

    # print(queryresult_returnpassenger[0].return_flight_seat.__dict__)
    return_flight_detail = [
        {
            "passenger_id": passenger.id,
            "assignment_number": passenger.assignment_number,
            "service_class": passenger.return_flight_seat.service_class.name,
            "cabin_position": passenger.return_flight_seat.cabin_position,
            "current_retail": FlightRetail.objects.get(
                Q(flight=passenger.reservation.return_flight)
                & Q(service_class=passenger.return_flight_seat.service_class)).current_retail
        }

        for passenger in queryresult_returnpassenger
    ]

    # get flight retail for each passenger associated with reservation departure flight
    total_cost_flight = sum([
        FlightRetail.objects.get(
            Q(flight=return_flight)
            & Q(service_class=passenger.return_flight_seat.service_class)).current_retail

        for passenger in queryresult_returnpassenger
    ])

    return_flight_summary = {
        "flight_id": reservation_main.return_flight.id,
        "plane_model": reservation_main.return_flight.plane.plane_model.model_name,
        "plane_make": reservation_main.return_flight.plane.plane_model.make_name,
        "departure_datetime": reservation_main.return_flight.departure_datetime,
        "arrival_datetime": reservation_main.return_flight.arrival_datetime,
        "number_of_passengers": queryresult_returnpassenger.count(),
        "total_cost_flight": total_cost_flight
    }

    context = {
        "reservation_id":request.GET['reservation_id'],
        "departure_flight_summary": departure_flight_summary,
        "return_flight_summary": return_flight_summary,
        "departure_flight_detail": departure_flight_detail,
        "return_flight_detail": return_flight_detail
    }

    return render(request,'reservations/my-trips/view.html', context=context)

def myTrips_view_submitEdit(request):

    # create new staging reservation
    reservation_main = Reservation_Main.objects.get(id=request.GET['reservation_id'])
    reservation_staging = Reservation_Staging.objects.create(
        number_of_passengers=reservation_main.number_of_passengers,
        round_trip=reservation_main.round_trip,
        customer=reservation_main.customer,
        departure_flight=reservation_main.departure_flight,
        return_flight=reservation_main.return_flight,
        reservation_main=reservation_main
    )

    # create new staging passengers
    passenger_main_queryresult = Passenger_Main.objects.filter(reservation_id=request.GET['reservation_id'])

    for passenger_main in passenger_main_queryresult:
        Passenger_Staging.objects.create(
            title=passenger_main.title,
            first_name=passenger_main.first_name,
            last_name=passenger_main.last_name,
            reservation=reservation_staging,
            departure_flight_seat=passenger_main.departure_flight_seat,
            return_flight_seat=passenger_main.return_flight_seat
        )

    # get session guid
    session_guid = uuid.uuid1()
    reservationSession = ReservationSession.objects.create(
        session_guid=session_guid,
        customer=reservation_main.customer,
        reservation_staging=reservation_staging)
    reservationSession.reservation_staging = reservation_staging

    # redirect to 'Edit' page
    return HttpResponseRedirect(reverse('reservations:my-trips/edit') + '?session_guid=' + str(session_guid))

def myTrips_getEdit(request):
    """
    generate a session_guid
    create new reservation session
    create new staging reservation
    create new staging passengers

    append a passenger_main_id column to the passenger_staging table
    because user already has a permanent reservation, how should their temporary reservation affect seat availability, etc?
    """

    reservationSession = ReservationSession.objects.get(session_guid=request.GET['session_guid'])
    reservation_staging = reservationSession.reservation_staging

    return_flight = reservation_staging.return_flight
    departure_flight = reservation_staging.departure_flight

    queryresult_departurepassenger = Passenger_Staging.objects \
        .filter(reservation_id=reservation_staging.id, departure_flight_seat__isnull=False) \
        .annotate(assignment_number=Window(DenseRank(), partition_by=[F('reservation')], order_by=F('id').asc()))

    departure_flight_detail = [
        {
            "passenger_id": passenger.id,
            "assignment_number": passenger.assignment_number,
            "service_class": passenger.departure_flight_seat.service_class.name,
            "cabin_position": passenger.departure_flight_seat.cabin_position,
            "current_retail": FlightRetail.objects.get(
                Q(flight=passenger.reservation.departure_flight)
                & Q(service_class=passenger.departure_flight_seat.service_class)).current_retail
        }
        for passenger in queryresult_departurepassenger
    ]

    # get flight retail for each passenger associated with reservation departure flight
    total_cost_flight = sum([
        FlightRetail.objects.get(
            Q(flight=departure_flight)
            & Q(service_class=passenger.departure_flight_seat.service_class)).current_retail

        for passenger in queryresult_departurepassenger
    ])

    departure_flight_summary = {
        "flight_id": reservation_staging.departure_flight.id,
        "plane_model": reservation_staging.return_flight.plane.plane_model.model_name,
        "plane_make": reservation_staging.return_flight.plane.plane_model.make_name,
        "departure_datetime": reservation_staging.departure_flight.departure_datetime,
        "arrival_datetime": reservation_staging.departure_flight.arrival_datetime,
        "number_of_passengers": queryresult_departurepassenger.count(),
        "total_cost_flight": total_cost_flight
    }

    # return flight context
    queryresult_returnpassenger = Passenger_Staging.objects \
        .filter(reservation_id=reservation_staging.id, return_flight_seat__isnull=False) \
        .annotate(assignment_number=Window(DenseRank(), partition_by=[F('reservation')], order_by=F('id').asc()))

    print(queryresult_returnpassenger[0].return_flight_seat.__dict__)
    return_flight_detail = [
        {
            "passenger_id": passenger.id,
            "assignment_number": passenger.assignment_number,
            "service_class": passenger.return_flight_seat.service_class.name,
            "cabin_position": passenger.return_flight_seat.cabin_position,
            "current_retail": FlightRetail.objects.get(
                Q(flight=passenger.reservation.return_flight)
                & Q(service_class=passenger.return_flight_seat.service_class)).current_retail
        }

        for passenger in queryresult_returnpassenger
    ]

    # get flight retail for each passenger associated with reservation departure flight
    total_cost_flight = sum([
        FlightRetail.objects.get(
            Q(flight=return_flight)
            & Q(service_class=passenger.return_flight_seat.service_class)).current_retail

        for passenger in queryresult_returnpassenger
    ])

    return_flight_summary = {
        "flight_id": reservation_staging.return_flight.id,
        "plane_model": reservation_staging.return_flight.plane.plane_model.model_name,
        "plane_make": reservation_staging.return_flight.plane.plane_model.make_name,
        "departure_datetime": reservation_staging.return_flight.departure_datetime,
        "arrival_datetime": reservation_staging.return_flight.arrival_datetime,
        "number_of_passengers": queryresult_returnpassenger.count(),
        "total_cost_flight": total_cost_flight
    }

    context = {
        "session_guid": reservationSession.session_guid,
        "departure_flight_summary": departure_flight_summary,
        "return_flight_summary": return_flight_summary,
        "departure_flight_detail": departure_flight_detail,
        "return_flight_detail": return_flight_detail
    }

    return render(request,'reservations/my-trips/edit.html', context)

def myTrips_getSearchFlight(request,flight_type):
    return render(request,'reservations/my-trips/search.html', context={'flight_type':flight_type, 'session_guid':request.GET['session_guid']})

def myTrips_submitSearchFlight(request, flight_type):
    reservationSession = ReservationSession.objects.get(session_guid=request.POST['session_guid'])

    if flight_type=='departure':
        reservationSession.departure_date = request.POST['flight_date']
        reservationSession.departure_airport_id = request.POST['departure_airport']
        reservationSession.save()

    if flight_type=='return':
        reservationSession.arrival_airport_id = request.POST['departure_airport']
        reservationSession.return_date = request.POST['flight_date']
        reservationSession.save()

    return HttpResponseRedirect(reverse('reservations:my-trips/select-flight',kwargs={'flight_type':flight_type}) + '?session_guid=' + request.POST['session_guid'])

def myTrips_getSelectFlight(request, flight_type):
    reservationSession = ReservationSession.objects.get(session_guid=request.GET['session_guid'])
    reservation_staging = reservationSession.reservation_staging


    if flight_type=='departure':
        flight_queryresults = Flight.objects.filter(
            departure_airport=reservationSession.departure_airport,
            departure_datetime__date=reservationSession.departure_date)

    if flight_type=='return':
        flight_queryresults = Flight.objects.filter(
            departure_airport=reservationSession.arrival_airport,
            departure_datetime__date=reservationSession.return_date)

    queryresults_passenger = Passenger_Staging.objects.filter(reservation=reservation_staging)

    #get current passenger retail
    original_flight_cost = sum([
        FlightRetail.objects.get(
            Q(flight=reservation_staging.return_flight)
            & Q(service_class=passenger.return_flight_seat.service_class)).current_retail

        for passenger in queryresults_passenger
    ])

    #get reservation passenger
    #get passenger flight seat
    passenger_staging_queryresults = Passenger_Staging.objects.filter(
        reservation=reservationSession.reservation_staging
    )

    FlightRetail.objects.filter(flight=reservation_staging.departure_flight)

    #get new passenger retail
    flights = [
        {
            'flight_id':flight.id,
            'departure_time':flight.departure_datetime,
            'arrival_time':flight.arrival_datetime,
            'plane_make':flight.plane.plane_model.make_name,
            'plane_model':flight.plane.plane_model.model_name,
            'new_flight_cost': as_currency(sum([
                FlightRetail.objects.get(
                    Q(flight=flight.id)
                    & Q(service_class=passenger.return_flight_seat.service_class)).current_retail

                for passenger in queryresults_passenger
            ])),
            'original_flight_cost':as_currency(original_flight_cost),
            'flight_cost_difference': as_currency(sum([
                FlightRetail.objects.get(
                    Q(flight=flight.id)
                    & Q(service_class=passenger.return_flight_seat.service_class)).current_retail

                for passenger in queryresults_passenger
            ]) - original_flight_cost)
        }

        for flight in flight_queryresults
    ]

    print(flights)

    #create 'flight' dictionary

    context = {
        'flight_type':flight_type,
        'session_guid':request.GET['session_guid'],
        'flights':flights
    }
    return render(request,'reservations/my-trips/select-flight.html',context)

def myTrips_submitSelectFlight(request, flight_type):
    """
    This method processes the request from the user to update the flight to the choice selected

    Logic:

    for each passenger in set of passengers
        get currently available seats on the new flight
        of that list, filter the seats that are of the passengers current service class
        if the available seat list is 0
            try for the next lowest service class
            return error response to user if there are no available service classes below the current
    """
    reservationSession = ReservationSession.objects.get(session_guid=request.POST['session_guid'])
    reservation_staging = reservationSession.reservation_staging

    # passengers
    passengers = Passenger_Staging.objects.filter(reservation=reservation_staging)

    #new flight to assign passengers to
    new_flight_id = request.POST['flight_id']
    print(new_flight_id)

    # #try assigning each passenger to available seats with current flight class;
    # #  if flight class isn't available on new plane, assign passenger a lower flight class
    # #  if lower flight class isn't available either, continue to next lower flight class
    # #  if no more flight classes left, return error
    # for passenger in passengers:
    #     availableFlightSeats = getAvailableFlightSeats(new_flight_id)
    #     availableFlightSeats = [
    #         {"serial_position":1, "seat_id":1, "service_class":"First Class"},
    #         {"serial_position":2, "seat_id":2, "service_class":"Economy"}]
    #     availableFlightSeats = sorted(
    #         [flightSeat for flightSeat in availableFlightSeats if flightSeat.service_class==1],
    #         key=lambda seat: seat.serial_position
    #
    #     )
    #     if len(availableFlightSeats)==0:


    #old flight passengers are currently assigned to
    print(reservation_staging.departure_flight_id)

    # update the reservation to the new flight
    if flight_type == 'departure':
        print(reservation_staging.__dict__)

    if flight_type == 'return':
        print(reservation_staging.__dict__)

    """
    END LOGIC TBC
    """
    return HttpResponseRedirect(reverse('reservations:my-trips/edit') + '?session_guid=' + request.POST['session_guid'])

def myTrips_getAddFlightSeat(request, flight_type):
    """
    Returns the contextualized template with seats available to add to reservation's flight

    CONTEXT

    flight_type
    flight
        departure_datetime
    seat
        cabin position
        service class
        cost
        seat_id

    LOGIC

    load context object

    get current flight type
    get current flight
    get current departure_datetime
    get (sorted) available seats and these attributes
        cabin_position
        service_class
        cost
        seat_id


    return response
    """
    context={'flight_type':flight_type,'session_guid':request.GET['session_guid']}


    reservationSession = ReservationSession.objects.get(session_guid=request.GET['session_guid'])
    reservation_staging = reservationSession.reservation_staging
    print(flight_type)
    print(reservation_staging.departure_flight_id)
    print(reservation_staging.departure_flight.departure_datetime)

    # flight seats
    reservationSession = ReservationSession.objects.get(session_guid=request.GET['session_guid'])
    reservation_staging = reservationSession.reservation_staging
    queryresults_passengers = Passenger_Staging.objects.filter(
        reservation__departure_flight=reservation_staging.departure_flight)
    queryresults_seats = PlaneSeat.objects \
        .filter(plane_model=reservation_staging.departure_flight.plane.plane_model) \
        .exclude(id__in=[passenger.return_flight_seat_id for passenger in queryresults_passengers if
                         passenger.return_flight_seat_id != None])

    context_seats = sorted([
        {
            "seat_id": seat.id,
            "serial_position": seat.serial_position,
            "cabin_position": seat.cabin_position,
            "service_class": seat.service_class.name,
            "cost": FlightRetail.objects.get(flight=reservation_staging.departure_flight,
                                             service_class=seat.service_class).current_retail
        }
        for seat in queryresults_seats
    ], key=lambda seat: seat["serial_position"])

    """
    END LOGIC TBC
    """

    return render(request, 'reservations/my-trips/add-flight-seat.html', context)

def myTrips_submitAddFlightSeat(request, flight_type):
    """
    Adds a new passenger_staging record with selected flight seat

    TEMPLATES

    source: reservations/my-trips/add-flight-seat.html
    destination: reservations/my-trips/edit.html

    CONTEXT

    seat_id
    flight_id
    session_guid
    flight_type

    LOGIC


    create new passenger_staging object
        if flight_type = departure, set departure flight seat to the submitted ID
        if flight_type = return, set passenger return flight seat to the submitted ID
    """

    # get current flight
    reservationSession = ReservationSession.objects.get(session_guid=request.POST['session_guid'])
    reservation_staging = Reservation_Staging.objects.get(id=reservationSession.reservation_staging_id)
    return_flight = reservation_staging.return_flight

    # get passengers for current flight
    return_flight_seats = [
        passenger.departure_flight_seat_id
        for passenger
        in Passenger_Staging.objects.filter(reservation__return_flight=return_flight)
    ]

    # check that reservation flight hasn't changed in the time the form was submitted
    if request.POST['flight'] == reservation_staging.return_flight.id:
        pass

    # check that submitted flight seat for reservation isn't already taken
    if request.POST['seat_id'] not in return_flight_seats:
        pass

    # create new passenger with departure seat assigned
    # Passenger_Staging.objects.create(
    #     reservation=reservation_staging,
    #     return_flight_seat_id=request.POST['seat_id']
    # )

    """END LOGIC TBC"""

    return HttpResponseRedirect(reverse('reservations:my-trips/edit') + '?session_guid=' + request.POST['session_guid'])

def myTrips_getUpdateFlightSeat(request, flight_type):
    """
    Returns contextualized template with seats available to update to for flight
    """


    """
    CONTEXT

    passenger_id
    session_guid
    flight
        departure_datetime
        id
    available_seats
        seat
            current_retail
            retail_delta
            service class
            cabin position
    """


    """
    LOGIC TBC
    """

    #passenger_id
    passenger_id = request.POST['passenger_id']
    session_guid = request.POST['session_guid']
    passenger_staging = Passenger_Staging.objects.get(passenger_id=passenger_id)
    flight = passenger_staging.reservation.departure_flight

    reservationSession = ReservationSession.objects.get(session_guid=request.GET['session_guid'])
    reservation_staging = reservationSession.reservation_staging
    queryresults_passengers = Passenger_Staging.objects.filter(
        reservation__return_flight=reservation_staging.return_flight)
    queryresults_seats = PlaneSeat.objects \
        .filter(plane_model=reservation_staging.return_flight.plane.plane_model) \
        .exclude(id__in=[passenger.return_flight_seat_id for passenger in queryresults_passengers if
                         passenger.return_flight_seat_id != None])

    passenger = Passenger_Staging.objects.get(id=request.GET['passenger_id'])
    current_seat_retail = FlightRetail.objects.get(
        service_class=passenger.return_flight_seat.service_class,
        flight=passenger.reservation.return_flight
    ).current_retail
    current_seat = passenger.return_flight_seat
    context_current_seat = {
        "seat_id": current_seat.id,
        "serial_position": current_seat.serial_position,
        "cabin_position": current_seat.cabin_position,
        "service_class": current_seat.service_class.name,
        "current_retail": current_seat_retail
    }

    context_seats = sorted([
        {
            "seat_id": seat.id,
            "serial_position": seat.serial_position,
            "cabin_position": seat.cabin_position,
            "service_class": seat.service_class.name,
            "current_retail": as_currency(FlightRetail.objects.get(flight=reservation_staging.return_flight,
                                                                   service_class=seat.service_class).current_retail),
            "retail_delta": as_currency(FlightRetail.objects.get(flight=reservation_staging.return_flight,
                                                                 service_class=seat.service_class).current_retail -
                                        context_current_seat["current_retail"])
        }
        for seat in queryresults_seats
    ], key=lambda seat: seat["serial_position"])

    context = {
        "flight": reservation_staging.return_flight,
        "passenger_id": passenger.id,
        "available_seats": context_seats,
        "current_seat": context_current_seat,
        "session_guid": request.GET['session_guid'],
        "flight_type": "return"
    }


    """
    END LOGIC TBC
    """

    context = {'flight_type':flight_type, 'session_guid':request.GET['session_guid']}
    return render(request,'reservations/my-trips/edit-flight-seat.html',context)

def myTrips_submitUpdateFlightSeat(request, flight_type):
    """
    Updates existing passenger_staging record with selected flight seat
    """

    """
    ROUTING
    
    source template:reservations/my-trips/edit-flight-seat.html
    """

    print(request.POST['seat_id'])
    print(request.POST['flight'])
    print(request.POST['passenger'])
    print(request.POST['session_guid'])

    passenger_staging = Passenger_Staging.objects.get(passenger_id=request.POST['passenger'])

    """
    LOGIC TBC
    """

    """
    END LOGIC TBC
    """

    return HttpResponseRedirect(reverse('reservations:my-trips/edit') + '?session_guid=' + request.POST['session_guid'])

def myTrips_getEditCheckOut(request):
    """

    """
    context = {'session_guid':request.GET['session_guid']}
    return render(request,'reservations/my-trips/edit-check-out.html',context)

def myTrips_submitEditCheckOut(request):
    """

    """
    reservationSession = ReservationSession.objects.get(session_guid=request.POST['session_guid'])
    reservation_main = reservationSession.reservation_staging.reservation_main
    print(reservationSession.reservation_staging)
    prompt()
    return HttpResponseRedirect(reverse('reservations:my-trips/edit-confirmation') + '?reservation_id=' + str(reservation_main.id))

def myTrips_getEditConfirmation(request):
    context = {'reservation_id':str(request.GET['reservation_id'])}
    return render(request,'reservations/my-trips/update-confirmation.html',context)

def checkIn_getSelectFlight(request):
    return render(request,'reservations/check-in/select-flight.html')

def checkIn_getReview(request):
    return render(request,'reservations/check-in/review.html', context={'flight_id':request.GET['flight_id']})

def checkIn_submitReview(request):
    return render(request,'reservations/check-in/confirmation.html',context={'flight_type':request.POST['flight_id'],'email_address':'shippeyben@gmail.com'})

def flightStatus_getSearchFlight(request):
    return render(request, 'reservations:flight-status/search-flight.html')

def flightStatus_getViewStatus(request):
    return render(request, 'reservations:flight-status/view.html')

def getFinalFlightConfirmation(request):

    reservationSession = ReservationSession.objects.get(session_guid=request.GET['session_guid'])
    reservation_staging = reservationSession.reservation_staging
    passenger_staging = Passenger_Staging.objects.filter(reservation=reservation_staging)
    reservation_main = reservation_staging.reservation_main

    reservationSession.delete()
    passenger_staging.delete()
    reservation_staging.delete()

    return render(request,'reservations/final-flight-confirmation.html',context={"reservation_number":reservation_main.id})

def getBookingCheckout(request):
    """
    return the booking checkout page
    """

    """
    reservations/flight-confirmation.html
    reservations/booking-check-out.html
    urls.py
    
    
    """

    reservationSession = ReservationSession.objects.get(session_guid=request.GET['session_guid'])
    reservation_staging = reservationSession.reservation_staging
    return_flight = reservation_staging.return_flight
    departure_flight = reservation_staging.departure_flight


    #departure flight context
    queryresult_departurepassenger = Passenger_Staging.objects \
        .filter(reservation_id=reservation_staging.id, departure_flight_seat__isnull=False) \
        .annotate(assignment_number=Window(DenseRank(), partition_by=[F('reservation')], order_by=F('id').asc()))

    departure_flight_detail = [
        {
            "passenger_id": passenger.id,
            "assignment_number": passenger.assignment_number,
            "service_class": passenger.departure_flight_seat.service_class.name,
            "cabin_position": passenger.departure_flight_seat.cabin_position,
            "current_retail": FlightRetail.objects.get(
                Q(flight=passenger.reservation.departure_flight)
                & Q(service_class=passenger.departure_flight_seat.service_class)).current_retail
        }
        for passenger in queryresult_departurepassenger
    ]

    # get flight retail for each passenger associated with reservation departure flight
    total_cost_flight = sum([
        FlightRetail.objects.get(
            Q(flight=departure_flight)
            & Q(service_class=passenger.departure_flight_seat.service_class)).current_retail

        for passenger in queryresult_departurepassenger
    ])

    departure_flight_summary = {
        "flight_id": reservation_staging.departure_flight.id,
        "plane_model": reservation_staging.return_flight.plane.plane_model.model_name,
        "plane_make": reservation_staging.return_flight.plane.plane_model.make_name,
        "departure_datetime": reservation_staging.departure_flight.departure_datetime,
        "arrival_datetime": reservation_staging.departure_flight.arrival_datetime,
        "number_of_passengers": queryresult_departurepassenger.count(),
        "total_cost_flight": total_cost_flight
    }

    # return flight context
    queryresult_returnpassenger = Passenger_Staging.objects \
        .filter(reservation_id=reservation_staging.id, return_flight_seat__isnull=False) \
        .annotate(assignment_number=Window(DenseRank(), partition_by=[F('reservation')], order_by=F('id').asc()))

    # get flight retail for each passenger associated with reservation departure flight
    total_cost_flight = sum([
        FlightRetail.objects.get(
            Q(flight=return_flight)
            & Q(service_class=passenger.return_flight_seat.service_class)).current_retail

        for passenger in queryresult_returnpassenger
    ])

    return_flight_summary = {
        "flight_id": reservation_staging.return_flight.id,
        "plane_model": reservation_staging.return_flight.plane.plane_model.model_name,
        "plane_make": reservation_staging.return_flight.plane.plane_model.make_name,
        "departure_datetime": reservation_staging.return_flight.departure_datetime,
        "arrival_datetime": reservation_staging.return_flight.arrival_datetime,
        "number_of_passengers": queryresult_returnpassenger.count(),
        "total_cost_flight": total_cost_flight
    }

    # return flight context
    queryresult_allpassengers = Passenger_Staging.objects \
        .filter(reservation_id=reservation_staging.id)\
        .annotate(assignment_number=Window(DenseRank(), partition_by=[F('reservation')], order_by=F('id').asc()))

    def handle_flightseat_exception(passenger_detail_field):
        try:
            return None
        except:
            return None

    passenger_detail = [
        {
            "passenger_id": passenger.id,
            "assignment_number":passenger.assignment_number,
            "return_service_class": None if passenger.return_flight_seat is None else passenger.return_flight_seat.service_class.name,
            "return_cabin_position": None if passenger.return_flight_seat is None else passenger.return_flight_seat.cabin_position,
            "departure_service_class": None if passenger.departure_flight_seat is None else passenger.departure_flight_seat,
            "departure_cabin_position": None if passenger.departure_flight_seat is None else passenger.departure_flight_seat.cabin_position
        }
        for passenger in queryresult_allpassengers
    ]

    total_cost_reservation = return_flight_summary['total_cost_flight'] + departure_flight_summary['total_cost_flight']

    context = {
        "session_guid": reservationSession.session_guid,
        "departure_flight_summary": departure_flight_summary,
        "return_flight_summary": return_flight_summary,
        "passenger_detail": passenger_detail,
        "total_cost_reservation": total_cost_reservation
    }

    return render(request,template_name='reservations/booking-check-out.html', context=context)

def submitBookingCheckout(request):
    """
    process flight booking submission
    """

    """
    -- create model and tables for payment information
    -- logic for submitting payment information 
    -- logic for handling passenger updates
    -- logic for handling creation of reservation final
    -- add link back to initial flight confirmation page              
    """

    """
    logic for storing payment information 
    
    - each sale is associated with a reservation_id/passenger_id/plane_seat_id combination
        - reason for doing this is to keep the data granular enough to make easier to work with reversal, etc.
    - credit card information isn't stored
    """

    """
    confirmation page html
    confirmation page redirect
    """

    reservationSession = ReservationSession.objects.get(session_guid=request.POST['session_guid'])
    reservation_staging = reservationSession.reservation_staging
    queryresults_passenger_staging = Passenger_Staging.objects.filter(reservation=reservation_staging)

    passenger_post_request_list = []
    for index in range(len(request.POST.getlist('passenger_id'))):
        passenger_post_request = {
            'title': request.POST.getlist('passenger_title')[index],
            'first_name': request.POST.getlist('passenger_first_name')[index],
            'last_name': request.POST.getlist('passenger_last_name')[index],
            'id': request.POST.getlist('passenger_id')[index]
        }
        passenger_post_request_list.append(passenger_post_request)

    for passenger in queryresults_passenger_staging:
        passenger.first_name =  list(filter(lambda x: int(x['id']) == passenger.id, passenger_post_request_list))[0]['first_name']
        passenger.last_name = list(filter(lambda x: int(x['id']) == passenger.id, passenger_post_request_list))[0]['last_name']
        passenger.title = list(filter(lambda x: int(x['id']) == passenger.id, passenger_post_request_list))[0]['title']
        passenger.save()

    print(reservation_staging.__dict__)
    # create reservation main object
    reservation_main = Reservation_Main.objects.create(
        customer=Customer.objects.get(pk=request.user.id),
        departure_flight_id=reservation_staging.departure_flight_id,
        return_flight_id=reservation_staging.return_flight_id,
        number_of_passengers=reservation_staging.number_of_passengers
    )

    reservation_staging.reservation_main = reservation_main
    reservation_staging.save()

    # for each passenger in reservation staging
    #   create passenger final objects
    #   assign first name, last name, title to passengers
    passenger_main_list = []
    for passenger_staging in queryresults_passenger_staging:
        passenger_main = Passenger_Main.objects.create(
            departure_flight_seat=passenger_staging.departure_flight_seat,
            return_flight_seat=passenger_staging.return_flight_seat,
            title=passenger_staging.title,
            first_name=passenger_staging.first_name,
            last_name=passenger_staging.last_name,
            reservation=reservation_main
        )
        passenger_main_list.append(passenger_main)



    """
    create a SalesTransaction object for each passenger/flight combination
    
    for each passenger in reservation
        get the departure flight seat cost
        get the return flight seat cost (if exists)
        create SalesTransaction object for departure flight
        create SalesTransaction object for return flight 
    """

    for passenger in passenger_main_list:
        departure_flight_retail = FlightRetail.objects.get(
            flight = reservation_main.departure_flight,
            service_class = passenger.departure_flight_seat.service_class
        ).current_retail

        if passenger.return_flight_seat is not None:
            return_flight_retail = FlightRetail.objects.get(
                flight=reservation_main.return_flight,
                service_class=passenger.return_flight_seat.service_class
            ).current_retail

        salesTransaction_departure = SalesTransaction.objects.create(
            amount=departure_flight_retail,
            reservation=passenger.reservation,
            passenger=passenger,
            flight_type="departure"
        )

        salesTransaction_return = SalesTransaction.objects.create(
            amount=return_flight_retail,
            reservation=passenger.reservation,
            passenger=passenger,
            flight_type="return"
        )

    return HttpResponseRedirect(reverse('reservations:final-flight-confirmation') + "?session_guid=" + reservationSession.session_guid)

def getDepartureFlightSeatUpdate(request):
    """
    reservations/update-flight-seat-reservation.html
    flight-confirmation.html
    flightConfirmation
    update-flight-seat-reservation/departure
    update-flight-seat-reservation/return

    send passenger id to update page
    get the current seat the passenger is assigned to

    cabin position
    service class
    current seat's flight retail
    new seat's flight retail

    """

    reservationSession = ReservationSession.objects.get(session_guid=request.GET['session_guid'])
    reservation_staging = reservationSession.reservation_staging
    queryresults_passengers = Passenger_Staging.objects.filter(
        reservation__departure_flight=reservation_staging.departure_flight)
    queryresults_seats = PlaneSeat.objects \
        .filter(plane_model=reservation_staging.departure_flight.plane.plane_model) \
        .exclude(id__in=[passenger.return_flight_seat_id for passenger in queryresults_passengers if
                         passenger.return_flight_seat_id != None])

    passenger = Passenger_Staging.objects.get(id=request.GET['passenger_id'])
    current_seat_retail = FlightRetail.objects.get(
        service_class=passenger.departure_flight_seat.service_class,
        flight = passenger.reservation.departure_flight
    ).current_retail
    current_seat = passenger.departure_flight_seat
    context_current_seat = {
        "seat_id": current_seat.id,
        "serial_position": current_seat.serial_position,
        "cabin_position": current_seat.cabin_position,
        "service_class": current_seat.service_class.name,
        "current_retail": current_seat_retail
    }

    context_seats = sorted([
        {
            "seat_id": seat.id,
            "serial_position": seat.serial_position,
            "cabin_position": seat.cabin_position,
            "service_class": seat.service_class.name,
            "current_retail": as_currency(FlightRetail.objects.get(flight=reservation_staging.departure_flight,
                                             service_class=seat.service_class).current_retail),
            "retail_delta": as_currency(FlightRetail.objects.get(flight=reservation_staging.departure_flight,
                                             service_class=seat.service_class).current_retail - context_current_seat["current_retail"])
        }
        for seat in queryresults_seats
    ], key=lambda seat: seat["serial_position"])

    context = {
        "flight": reservation_staging.departure_flight,
        "passenger_id":passenger.id,
        "available_seats": context_seats,
        "current_seat": context_current_seat,
        "session_guid": request.GET['session_guid'],
        "flight_type": "departure"
    }

    return render(request, context=context, template_name='reservations/update-flight-seat-reservation.html')

def submitDepartureFlightSeatUpdate(request):
    # get current flight
    # print(request.POST['session_guid'])
    reservationSession = ReservationSession.objects.get(session_guid=request.POST['session_guid'])
    reservation_staging = Reservation_Staging.objects.get(id=reservationSession.reservation_staging_id)
    departure_flight = reservation_staging.departure_flight

    # get passengers for current flight
    departure_flight_seats = [
        passenger.departure_flight_seat_id
        for passenger
        in Passenger_Staging.objects.filter(reservation__departure_flight=departure_flight)
    ]

    # check that reservation flight hasn't changed in the time the form was submitted
    if request.POST['flight'] != str(reservation_staging.departure_flight.id):
        print('test 1')
        print('POST flight ' + str(request.POST['flight']))
        print('Reservation flight ' + str(reservation_staging.departure_flight.id))
        return

    # check that submitted flight seat for reservation isn't already taken
    if request.POST['seat_id'] in departure_flight_seats:
        return

    passenger = Passenger_Staging.objects.get(id=int(request.POST['passenger']))
    passenger.departure_flight_seat_id = request.POST['seat_id']
    passenger.save()
    print(request.POST.__dict__)

    return HttpResponseRedirect(reverse('reservations:flight-confirmation') + '?session_guid=' + request.POST['session_guid'])




def getReturnFlightSeatUpdate(request):
    """
    reservations/update-flight-seat-reservation.html
    flight-confirmation.html
    flightConfirmation
    update-flight-seat-reservation/departure
    update-flight-seat-reservation/return

    send passenger id to update page
    get the current seat the passenger is assigned to

    cabin position
    service class
    current seat's flight retail
    new seat's flight retail

    """

    reservationSession = ReservationSession.objects.get(session_guid=request.GET['session_guid'])
    reservation_staging = reservationSession.reservation_staging
    queryresults_passengers = Passenger_Staging.objects.filter(
        reservation__return_flight=reservation_staging.return_flight)
    queryresults_seats = PlaneSeat.objects \
        .filter(plane_model=reservation_staging.return_flight.plane.plane_model) \
        .exclude(id__in=[passenger.return_flight_seat_id for passenger in queryresults_passengers if
                         passenger.return_flight_seat_id != None])

    passenger = Passenger_Staging.objects.get(id=request.GET['passenger_id'])
    current_seat_retail = FlightRetail.objects.get(
        service_class=passenger.return_flight_seat.service_class,
        flight = passenger.reservation.return_flight
    ).current_retail
    current_seat = passenger.return_flight_seat
    context_current_seat = {
        "seat_id": current_seat.id,
        "serial_position": current_seat.serial_position,
        "cabin_position": current_seat.cabin_position,
        "service_class": current_seat.service_class.name,
        "current_retail": current_seat_retail
    }

    context_seats = sorted([
        {
            "seat_id": seat.id,
            "serial_position": seat.serial_position,
            "cabin_position": seat.cabin_position,
            "service_class": seat.service_class.name,
            "current_retail": as_currency(FlightRetail.objects.get(flight=reservation_staging.return_flight,
                                             service_class=seat.service_class).current_retail),
            "retail_delta": as_currency(FlightRetail.objects.get(flight=reservation_staging.return_flight,
                                             service_class=seat.service_class).current_retail - context_current_seat["current_retail"])
        }
        for seat in queryresults_seats
    ], key=lambda seat: seat["serial_position"])

    context = {
        "flight": reservation_staging.return_flight,
        "passenger_id":passenger.id,
        "available_seats": context_seats,
        "current_seat": context_current_seat,
        "session_guid": request.GET['session_guid'],
        "flight_type": "return"
    }

    return render(request, context=context, template_name='reservations/update-flight-seat-reservation.html')

def submitReturnFlightSeatUpdate(request):
    # get current flight
    # print(request.POST['session_guid'])
    reservationSession = ReservationSession.objects.get(session_guid=request.POST['session_guid'])
    reservation_staging = Reservation_Staging.objects.get(id=reservationSession.reservation_staging_id)
    return_flight = reservation_staging.return_flight

    # get passengers for current flight
    return_flight_seats = [
        passenger.return_flight_seat_id
        for passenger
        in Passenger_Staging.objects.filter(reservation__return_flight=return_flight)
    ]

    # check that reservation flight hasn't changed in the time the form was submitted
    if request.POST['flight'] != str(reservation_staging.return_flight.id):
        print('test 1')
        print('POST flight ' + str(request.POST['flight']))
        print('Reservation flight ' + str(reservation_staging.return_flight.id))
        return

    # check that submitted flight seat for reservation isn't already taken
    if request.POST['seat_id'] in return_flight_seats:
        return

    passenger = Passenger_Staging.objects.get(id=int(request.POST['passenger']))
    passenger.return_flight_seat_id = request.POST['seat_id']
    passenger.save()
    print(request.POST.__dict__)

    return HttpResponseRedirect(reverse('reservations:flight-confirmation') + '?session_guid=' + request.POST['session_guid'])

def submitDepartureFlightSeatDeletion(request):
    reservationSession = ReservationSession.objects.get(session_guid=request.POST['session_guid'])
    reservation_staging = Reservation_Staging.objects.get(pk=reservationSession.reservation_staging_id)

    if reservation_staging.departure_flight_id != int(request.POST['flight']):
        return

    passenger = Passenger_Staging.objects.get(id=request.POST['passenger_id'])
    passenger.departure_flight_seat_id = None
    passenger.save()

    return HttpResponseRedirect(reverse('reservations:flight-confirmation') + '?session_guid=' + request.POST['session_guid'])

def submitReturnFlightSeatDeletion(request):
    reservationSession = ReservationSession.objects.get(session_guid=request.POST['session_guid'])
    reservation_staging = Reservation_Staging.objects.get(pk=reservationSession.reservation_staging_id)

    if reservation_staging.return_flight_id != int(request.POST['flight']):
        return

    passenger = Passenger_Staging.objects.get(id=request.POST['passenger_id'])
    passenger.return_flight_seat_id = None
    passenger.save()

    return HttpResponseRedirect(reverse('reservations:flight-confirmation') + '?session_guid=' + request.POST['session_guid'])


def submitDepartureFlightSeatAddition(request):
    """
    check if submitted flight seat is already assigned to an existing passenger
    if not - create new passenger record for reservation
    """
    #submitted flight seat
    print(request.POST['seat_id'])

    #get current flight
    reservationSession = ReservationSession.objects.get(session_guid=request.POST['session_guid'])
    reservation_staging = Reservation_Staging.objects.get(id=reservationSession.reservation_staging_id)
    departure_flight = reservation_staging.departure_flight

    #get passengers for current flight
    departure_flight_seats = [
        passenger.departure_flight_seat_id
        for passenger
        in Passenger_Staging.objects.filter(reservation__departure_flight=departure_flight)
        ]

    #check that reservation flight hasn't changed in the time the form was submitted
    if request.POST['flight'] == reservation_staging.departure_flight.id:
        pass

    #check that submitted flight seat for reservation isn't already taken
    if request.POST['seat_id'] not in departure_flight_seats:
        pass

    #create new passenger with departure seat assigned
    Passenger_Staging.objects.create(
        reservation = reservation_staging,
        departure_flight_seat_id= request.POST['seat_id']
    )

    #return the user back to the initial confirmation page
    return HttpResponseRedirect(reverse('reservations:flight-confirmation') + '?session_guid=' + request.POST['session_guid'])


def getDepartureFlightSeatAddition(request):
    """
    templates:
     add-flight-seat-reservation.html
     flight-confirmation.html

    url:
     /add-flight-seat-reservation
     /flight-confirmation

    considerations:
     what happens if seat displayed on 'add new passenger' page is taken
      in the time the user is on the page?
    """

    reservationSession = ReservationSession.objects.get(session_guid=request.GET['session_guid'])
    reservation_staging = reservationSession.reservation_staging
    queryresults_passengers = Passenger_Staging.objects.filter(reservation__departure_flight=reservation_staging.departure_flight)
    queryresults_seats = PlaneSeat.objects\
        .filter(plane_model=reservation_staging.departure_flight.plane.plane_model)\
        .exclude(id__in=[passenger.return_flight_seat_id for passenger in queryresults_passengers if passenger.return_flight_seat_id != None])

    context_seats = sorted([
        {
            "seat_id":seat.id,
            "serial_position":seat.serial_position,
            "cabin_position":seat.cabin_position,
            "service_class": seat.service_class.name,
            "cost": FlightRetail.objects.get(flight=reservation_staging.departure_flight, service_class=seat.service_class).current_retail
         }
        for seat in queryresults_seats
    ], key=lambda seat: seat["serial_position"])

    context = {
        "flight":reservation_staging.departure_flight,
        "available_seats":context_seats,
        "session_guid": request.GET['session_guid'],
        "flight_type":"departure"
    }

    return render(request,context=context, template_name='reservations/add-flight-seat-reservation.html')

def submitReturnFlightSeatAddition(request):
    """
    check if submitted flight seat is already assigned to an existing passenger
    if not - create new passenger record for reservation
    """
    #submitted flight seat
    print(request.POST['seat_id'])

    #get current flight
    reservationSession = ReservationSession.objects.get(session_guid=request.POST['session_guid'])
    reservation_staging = Reservation_Staging.objects.get(id=reservationSession.reservation_staging_id)
    return_flight = reservation_staging.return_flight

    #get passengers for current flight
    return_flight_seats = [
        passenger.departure_flight_seat_id
        for passenger
        in Passenger_Staging.objects.filter(reservation__return_flight=return_flight)
        ]

    #check that reservation flight hasn't changed in the time the form was submitted
    if request.POST['flight'] == reservation_staging.return_flight.id:
        pass

    #check that submitted flight seat for reservation isn't already taken
    if request.POST['seat_id'] not in return_flight_seats:
        pass

    #create new passenger with departure seat assigned
    Passenger_Staging.objects.create(
        reservation = reservation_staging,
        return_flight_seat_id= request.POST['seat_id']
    )

    #return the user back to the initial confirmation page
    return HttpResponseRedirect(reverse('reservations:flight-confirmation') + '?session_guid=' + request.POST['session_guid'])

def getReturnFlightSeatAddition(request):
    """
    templates:
     add-flight-seat-reservation.html
     flight-confirmation.html

    url:
     /add-flight-seat-reservation
     /flight-confirmation

    considerations:
     what happens if seat displayed on 'add new passenger' page is taken
      in the time the user is on the page?
    """

    #get all the flight seats that are assigned on flight
    reservationSession = ReservationSession.objects.get(session_guid=request.GET['session_guid'])
    reservation_staging = reservationSession.reservation_staging
    queryresults_passengers = Passenger_Staging.objects.filter(reservation__return_flight=reservation_staging.return_flight)
    queryresults_seats = PlaneSeat.objects\
        .filter(plane_model=reservation_staging.return_flight.plane.plane_model)\
        .exclude(id__in=[passenger.return_flight_seat_id for passenger in queryresults_passengers if passenger.return_flight_seat_id != None])

    context_seats = sorted([
        {
            "seat_id":seat.id,
            "serial_position":seat.serial_position,
            "cabin_position":seat.cabin_position,
            "service_class": seat.service_class.name,
            "cost": FlightRetail.objects.get(flight=reservation_staging.return_flight, service_class=seat.service_class).current_retail
         }
        for seat in queryresults_seats
    ], key=lambda seat: seat["serial_position"])
    context = {
        "flight":reservation_staging.return_flight,
        "available_seats":context_seats,
        "session_guid": request.GET['session_guid'],
        "flight_type":"return"
    }

    return render(request,context=context, template_name='reservations/add-flight-seat-reservation.html')

def getFlightConfirmation(request):
    """
    Initial Flight Confirmation Page:
    """
    """
    Resources:

    template: templates/reservations/flight-confirmation.html
    url conf: reservations/urls.py
    """

    reservationSession = ReservationSession.objects.get(session_guid=request.GET['session_guid'])
    reservation_staging = reservationSession.reservation_staging
    return_flight = reservation_staging.return_flight
    departure_flight = reservation_staging.departure_flight


    #departure flight context
    # departure passengers linked to reservation
    queryresult_departurepassenger = Passenger_Staging.objects\
        .filter(reservation_id=reservation_staging.id, departure_flight_seat__isnull=False)\
        .annotate(assignment_number=Window(DenseRank(), partition_by=[F('reservation')], order_by=F('id').asc()))

    departure_flight_detail = [
        {
            "passenger_id": passenger.id,
            "assignment_number":passenger.assignment_number,
            "service_class": passenger.departure_flight_seat.service_class.name,
            "cabin_position": passenger.departure_flight_seat.cabin_position,
            "current_retail": FlightRetail.objects.get(
                Q(flight=passenger.reservation.departure_flight)
                & Q(service_class=passenger.departure_flight_seat.service_class)).current_retail
        }
        for passenger in queryresult_departurepassenger
    ]

    # get flight retail for each passenger associated with reservation departure flight
    total_cost_flight = sum([
        FlightRetail.objects.get(
            Q(flight=departure_flight)
            & Q(service_class=passenger.departure_flight_seat.service_class)).current_retail

        for passenger in queryresult_departurepassenger
    ])

    departure_flight_summary = {
        "flight_id":reservation_staging.departure_flight.id,
        "plane_model": reservation_staging.return_flight.plane.plane_model.model_name,
        "plane_make": reservation_staging.return_flight.plane.plane_model.make_name,
        "departure_datetime":reservation_staging.departure_flight.departure_datetime,
        "arrival_datetime":reservation_staging.departure_flight.arrival_datetime,
        "number_of_passengers":queryresult_departurepassenger.count(),
        "total_cost_flight":total_cost_flight
    }

    #return flight context
    queryresult_returnpassenger = Passenger_Staging.objects\
        .filter(reservation_id=reservation_staging.id, return_flight_seat__isnull=False)\
        .annotate(assignment_number = Window(DenseRank(),partition_by=[F('reservation')],order_by=F('id').asc()))

    print(queryresult_returnpassenger[0].return_flight_seat.__dict__)
    return_flight_detail = [
            {
                "passenger_id": passenger.id,
                "assignment_number":passenger.assignment_number,
                "service_class": passenger.return_flight_seat.service_class.name,
                "cabin_position": passenger.return_flight_seat.cabin_position,
                "current_retail": FlightRetail.objects.get(
                    Q(flight=passenger.reservation.return_flight)
                    & Q(service_class=passenger.return_flight_seat.service_class)).current_retail
            }

        for passenger in queryresult_returnpassenger
    ]

    # get flight retail for each passenger associated with reservation departure flight
    total_cost_flight = sum([
        FlightRetail.objects.get(
            Q(flight=return_flight)
            & Q(service_class=passenger.return_flight_seat.service_class)).current_retail

        for passenger in queryresult_returnpassenger
    ])

    return_flight_summary = {
        "flight_id": reservation_staging.return_flight.id,
        "plane_model": reservation_staging.return_flight.plane.plane_model.model_name,
        "plane_make": reservation_staging.return_flight.plane.plane_model.make_name,
        "departure_datetime": reservation_staging.return_flight.departure_datetime,
        "arrival_datetime": reservation_staging.return_flight.arrival_datetime,
        "number_of_passengers": queryresult_returnpassenger.count(),
        "total_cost_flight": total_cost_flight
    }

    context = {
        "session_guid": reservationSession.session_guid,
        "departure_flight_summary":departure_flight_summary,
        "return_flight_summary":return_flight_summary,
        "departure_flight_detail":departure_flight_detail,
        "return_flight_detail":return_flight_detail
    }

    return render(request,context=context,template_name='reservations/flight-confirmation.html')

def submitReturnFlightChoice(request):
    """method should be roughly the same as departure submission"""
    reservationSession = ReservationSession.objects.get(session_guid=request.POST['session_guid'])
    reservation_staging = reservationSession.reservation_staging
    submitted_flight_id = int(json.loads(request.POST['flight_class'])['flight_id'])
    submitted_service_class_id = int(json.loads(request.POST['flight_class'])['class_id'])
    reservation_staging.return_flight_id = submitted_flight_id
    reservation_staging.save()

    def getNextAvailableFlightSeat():
        # query 1: all flight seats for given flight and service class
        queryresult_allflightseats1 = Flight.objects.get(pk=reservation_staging.return_flight_id)  # get submitted departure flight
        queryresult_allflightseats2 = Plane.objects.get(pk=queryresult_allflightseats1.plane_id)  # get plane for submitted departure flight
        queryresult_allflightseats3 = PlaneModel.objects.get(pk=queryresult_allflightseats2.plane_model_id)  # get plane model for departure flight plane
        queryresult_allflightseats = PlaneSeat.objects.filter(plane_model_id=queryresult_allflightseats3.id, service_class_id=submitted_service_class_id)  # get plane seats for plane model

        # query 2: all flight seats currently linked to passengers

        # seats occupied by *valid* staged reservation
        """
        a staged reservation is valid if created less than 15 minutes ago; 

        i.e. if TIME NOW (UTC) is greater than 15 minutes since TIME CREATE (UTC) then the reservation is no longer valid

        am I logging dates as UTC?

        comparing datetime fields in python?
        """
        queryresult_occupiedseats1 = Reservation_Staging.objects.filter(
            return_flight_id=queryresult_allflightseats1.id)  # get all reservations for selected departure flight
        queryresult_occupiedseats2 = \
            [reservation_staging for reservation_staging in queryresult_occupiedseats1 if reservation_staging.isvalid()]
        queryresult_occupiedseats3 = Passenger_Staging.objects.filter(
            reservation__in=queryresult_occupiedseats2)  # get passengers for reservations for selected departure flight

        # seats occupied by permanent reservations
        queryresult_occupiedseats4 = Reservation_Main.objects.filter(
            return_flight_id=queryresult_allflightseats1.id)  # get all reservations for selected departure flight
        queryresult_occupiedseats5 = Passenger_Main.objects.filter(
            reservation__in=queryresult_occupiedseats4)  # get passengers for reservations for selected departure flight

        queryresult_occupiedseats = PlaneSeat.objects.filter( # get plane seats for reservation passengers
            Q(pk__in=[passenger.return_flight_seat_id for passenger in queryresult_occupiedseats3])
            | Q(pk__in=[passenger.return_flight_seat_id for passenger in queryresult_occupiedseats5]))

        availableflightseats = set(queryresult_allflightseats) - set(queryresult_occupiedseats)
        sorted_availableflightseats = sorted(availableflightseats, key=lambda flightseat: flightseat.serial_position)
        return sorted_availableflightseats[0]

    reservationPassengers = Passenger_Staging.objects.filter(reservation=reservation_staging)

    for passenger in reservationPassengers:
        nextAvailableFlightSeat = getNextAvailableFlightSeat()
        passenger.return_flight_seat_id = nextAvailableFlightSeat
        passenger.save()

    return HttpResponseRedirect(reverse('reservations:flight-confirmation') + '?session_guid=' + reservationSession.session_guid)

def submitDepartureFlightChoice(request):

    reservationSession = ReservationSession.objects.get(session_guid=request.POST['session_guid'])
    reservation_staging = reservationSession.reservation_staging
    submitted_flight_id = int(json.loads(request.POST['flight_class'])['flight_id'])
    submitted_service_class_id = int(json.loads(request.POST['flight_class'])['class_id'])
    reservation_staging.departure_flight_id = submitted_flight_id
    reservation_staging.save()

    def getNextAvailableFlightSeat():
        #query 1: all flight seats for given flight and service class
        queryresult_allflightseats1 = Flight.objects.get(pk=reservation_staging.departure_flight_id) #get submitted departure flight
        queryresult_allflightseats2 = Plane.objects.get(pk=queryresult_allflightseats1.plane_id) #get plane for submitted departure flight
        queryresult_allflightseats3 = PlaneModel.objects.get(pk=queryresult_allflightseats2.plane_model_id) #get plane model for departure flight plane
        queryresult_allflightseats = PlaneSeat.objects.filter(plane_model_id=queryresult_allflightseats3.id, service_class_id=submitted_service_class_id) #get plane seats for plane model

        #query 2: all flight seats currently linked to passengers

        #seats occupied by *valid* staged reservation
        """
        a staged reservation is valid if created less than 15 minutes ago; 
        
        i.e. if TIME NOW (UTC) is greater than 15 minutes since TIME CREATE (UTC) then the reservation is no longer valid
        
        am I logging dates as UTC?
        
        comparing datetime fields in python?
        """
        queryresult_occupiedseats1 = Reservation_Staging.objects.filter(departure_flight_id=queryresult_allflightseats1.id) #get all reservations for selected departure flight
        queryresult_occupiedseats2 = [reservation_staging for reservation_staging in queryresult_occupiedseats1 if reservation_staging.isvalid()]
        queryresult_occupiedseats3 = Passenger_Staging.objects.filter(reservation__in = queryresult_occupiedseats2) #get passengers for reservations for selected departure flight

        #seats occupied by permanent reservations
        queryresult_occupiedseats4 = Reservation_Main.objects.filter(departure_flight_id=queryresult_allflightseats1.id)  #get all reservations for selected departure flight
        queryresult_occupiedseats5 = Passenger_Main.objects.filter(reservation__in=queryresult_occupiedseats4)  # get passengers for reservations for selected departure flight

        queryresult_occupiedseats = PlaneSeat.objects.filter(
            Q(pk__in=[passenger.departure_flight_seat_id for passenger in queryresult_occupiedseats3])
            | Q(pk__in=[passenger.departure_flight_seat_id for passenger in queryresult_occupiedseats5])) #get plane seats for reservation passengers

        availableflightseats = set(queryresult_allflightseats) - set(queryresult_occupiedseats)
        sorted_availableflightseats = sorted(availableflightseats, key=lambda flightseat: flightseat.serial_position)
        return sorted_availableflightseats[0]

    reservationPassengers = Passenger_Staging.objects.filter(reservation=reservation_staging)

    for passenger in reservationPassengers:
        nextAvailableFlightSeat = getNextAvailableFlightSeat()
        passenger.departure_flight_seat_id = nextAvailableFlightSeat
        passenger.save()


    """
    Initial Flight Confirmation Page:
    """

    if reservationSession.round_trip == "on":
        #redirect to return flight page
        return HttpResponseRedirect(reverse('reservations:choose-return-flight') + '?session_guid=' + reservationSession.session_guid)
    else:
        #redirect to flight confirmation page
        return HttpResponse('Submit Flight Choice Page')

def reservationConfirmation(request):
    pass

def reservationCheckout(request):
    pass

def reservationFinalConfirmation(request):
    pass

def chooseReturnFlight(request):
    """
    UPDATES NEEDED


    """
    reservationSession = ReservationSession.objects.get(session_guid=request.GET['session_guid'])

    # get flights that match the reservation_staging search criteria
    flights_staging = Flight.objects.filter(
        arrival_airport= reservationSession.departure_airport,
        departure_airport= reservationSession.arrival_airport,
        departure_datetime__date=reservationSession.return_date
    )

    flight_retails_staging1 = FlightRetail.objects.filter(flight__in=flights_staging)

    flights = []
    for flight in flights_staging:
        flight_retails_staging2 = flight_retails_staging1.filter(flight_id=flight.id)
        flight_retails = {}
        for flight_retail in flight_retails_staging2:
            flight_retails[flight_retail.service_class_id] = flight_retail.current_retail
        flights.append({"flight": flight, "flight_retail_by_service_class": flight_retails})

    template = loader.get_template('reservations/choose-return-flight.html')
    context = {
        'flights': flights,
        'number_of_passengers': reservationSession.number_of_passengers,
        'round_trip': reservationSession.round_trip,
        'departure_date': reservationSession.departure_date,
        'return_date': reservationSession.return_date,
        'departure_airport': reservationSession.departure_airport,
        'arrival_airport': reservationSession.arrival_airport,
        'session_guid': request.GET['session_guid']
    }
    # return flights to user that match criteria on the reservation_staging object
    return HttpResponse(template.render(context, request))

def chooseDepartureFlight(request):
    """
    UPDATES NEEDED

    return only flights that have seats available
    """

    reservationSession = ReservationSession.objects.get(session_guid=request.GET['session_guid'])

    #get flights that match the reservation_staging search criteria
    flights_staging = Flight.objects.filter(
        arrival_airport=reservationSession.arrival_airport,
        departure_airport=reservationSession.departure_airport,
        departure_datetime__date=reservationSession.departure_date
    )


    flight_retails_staging1 = FlightRetail.objects.filter(flight__in=flights_staging)

    flights = []
    for flight in flights_staging:
        flight_retails_staging2 = flight_retails_staging1.filter(flight_id=flight.id)
        flight_retails = {}
        for flight_retail in flight_retails_staging2:
            flight_retails[flight_retail.service_class_id] = flight_retail.current_retail
        flights.append({"flight":flight, "flight_retail_by_service_class":flight_retails})


    template = loader.get_template('reservations/choose-departure-flight.html')
    context = {
        'flights': flights,
        'number_of_passengers': reservationSession.number_of_passengers,
        'round_trip': reservationSession.round_trip,
        'departure_date': reservationSession.departure_date,
        'return_date': reservationSession.return_date,
        'departure_airport':reservationSession.departure_airport,
        'arrival_airport': reservationSession.arrival_airport,
        'session_guid':request.GET['session_guid']
    }
    # return flights to user that match criteria on the reservation_staging object
    return HttpResponse(template.render(context, request))


"""
If round_trip = TRUE
	User goes to Return Flight page
If round_trip = FALSE
	User goes to the Confirmation page
	If User agrees with the current selections
		Continues onto Check-out Page
		Provides names for each of the Passengers on the flight
		User provides payment information
		User clicks SUBMIT and the flight reservation is made
"""

# GET/search-flights
def searchFlights(request):

    """
    """

    """
    Return results page back from search query

     -- Check that user is logged-in
      - If not already logged-in, redirect them to the sign-in page
      - If else, continue
      - (For now, assume the user is logged in)
     -- Generate SESSION GUID for current flight on the client side
     -- Create RESERVATION SESSION object and write this to the database
     -= Return Flight Results page w/given Session ID as URL Parameter
      - User chooses their departure flight
      - User chooses their return flight
     - When reservation is 'finalized'
      - The SESSION GUID is invalidated
      - Changes are committed as new RESERVATION object is created

    Follow-up concern:

     - If the user wants to update their reservation - should the same external GUID be presented?
     - Keep the SESSION object as a 'staging' reservation object and only commit changes to main
      RESERVATION object when those changes are finalized

    How to keep only one of the parameters visible when returning response to user? I want to present
     only the session_id parameter but submit the other values to the database; and store on the SESSION object

     - Option 1: Keep the extra URL parameters and ignore those parameters in actual response processing
     - Option 2: Get SESSION ID from server in AJAX request and make secondary GET request using obtained SESSION ID
     - Option 3: HttpResponseRedirect with URL parameter tacked on
    """

    """
    REQUEST contains SESSION GUID that contains the state of the search criteria
    SESSION extends the RESERVATION object and the SESSION object merges with the RESERVATION object 
     when changes are finalized

    Next steps:

     - Create SESSION object with Reservation 'staging', search request information stored on object
     - Create flight-results endpoint to process and return information based session_guid
     - Have searchFlights function redirect to new flight-results endpoint
     - Create flight-results/return endpoint to process and return information based on session_guid
     - Create logic for CONFIRMATION page to create a new RESERVATION object based on the SESSION object
    """

    if request.method == "POST":

        #create reservation_staging object
        reservationSession = ReservationSession.objects.create(
            reservation_staging=None,
            customer= Customer.objects.get(pk=request.user.id),
            departure_airport= Airport.objects.get(pk=request.POST['departure_airport']),
            arrival_airport=Airport.objects.get(pk=request.POST['arrival_airport']),
            departure_date=request.POST['departure_date'],
            return_date=request.POST['return_date'],
            #ISSUE: round_trip does not exist on the POST object if round_trip is off in HTML form
            round_trip=request.POST['round_trip'],
            session_guid=request.POST['session_guid'],
            number_of_passengers=request.POST['number_of_passengers']
        )

        reservation_staging = Reservation_Staging.objects.create(
            customer=Customer.objects.get(user_ptr_id=request.user.id),
            number_of_passengers=str(reservationSession.number_of_passengers),

            round_trip=True if reservationSession.round_trip == "on" else False
            )

        reservationSession.reservation_staging = reservation_staging
        reservationSession.save()

        # create passenger objects tied to reservation_staging object
        # assign service class to each of the passenger objects
        """
        drop existing matched passenger_staging records if any
        create passengers
            assigned seats must be service class matching that of reservation
            assigned seats must be on plane matching that of flight

        create passenger objects if PASSENGER COUNT > count existing PASSENGERS
        OR
        drop all matching passenger objects and re-create? I think it can be assumed that if the
         user visits this page, they were uncertain about the booking to begin with; plus we need to
         free up space for the flight they've unselected so that other customers may have the opportunity
         to purchase a flight

        however, what if the customer only wants to change the flight for departure and keep the return flight
         as the previous selection? Isn't it a little bit reckless to just drop all existing data? 
        """
        # create passengers
        for index in range(int(reservationSession.number_of_passengers)):
            passenger = Passenger_Staging.objects.create(reservation=reservation_staging)

        #redirect user to search results page with SESSION GUID as URL parameter
        return HttpResponseRedirect(reverse('reservations:choose-departure-flight') + '?session_guid=' + request.POST['session_guid'])


