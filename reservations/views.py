from django.shortcuts import HttpResponse, render, reverse, HttpResponseRedirect
from django.db.models import Q
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login
from django.template import loader

import json
from datetime import date

from prompt_toolkit import prompt

from .models_customers import *


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


def userLogin(request):
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


def bookReservation(request):
    if request.method == "GET":
        return render(request, "reservations/book.html")


# def chooseFlight(request):
#     """
#     Considerations:
#      - Where to cache the user's flight selection?
#       - Should the Reservation_Staging object carry the flight selection information?
#       - Should I create a separate 'Search Session' object and store the search session information there, rather?
#        I.e. keep the SEARCH information separate from the RESERVATION information
#     """
#
#     # User selects a flight and a Reservation_Staging object is created
#     # If round_trip = on, the user is taken to the Departure page
#     # Else, user is taken to the Confirmation Page
#
#     template = loader.get_template('reservations/choose-departure-flight.html')
#     context = {'session_guid':request.GET['session_guid']}
#     return HttpResponse(template.render(context, request))


def flightConfirmation(request):
    """
    Initial Flight Confirmation Page:
    """
    """
    Resources:

    template: templates/reservations/flight-confirmation.html
    url conf: reservations/urls.py
    """

    """
    Information needed:

     - Departure Flight 
     - Departure Flight Passengers 
     - Departure Flight Cost
     - Return Flight 
     - Return Flight Passengers
     - Return Flight Cost

    reservation session --> reservation staging --> passengers
    reservation session --> reservation staging --> flight
    """
    reservationSession = ReservationSession.objects.get(session_guid=request.GET['session_guid'])
    reservation_staging = reservationSession.reservation_staging
    return_flight = reservation_staging.return_flight
    departure_flight = reservation_staging.departure_flight

    # departure passengers linked to reservation
    queryresult_passenger = Passenger_Staging.objects.filter(reservation_id=reservation_staging.id)

    #flight retails linked to departure flight
    queryresult_flightretail = FlightRetail.objects.filter(flight_id=reservation_staging.departure_flight_id)

    print(queryresult_passenger[0].departure_flight_seat.service_class.name)
    print(queryresult_flightretail[0].__dict__)
    """
    create flight seat detail list of dictionaries
    
    Assignment #
    Passenger ID (internally kept)
    Service Class
    Cabin Position
    Seat Cost (US $)
    
    {'_state': <django.db.models.base.ModelState object at 0x000001C0C13DF9E8>, 
        'id': 170, 
        'departure_flight_seat_id': 2, 
        'return_flight_seat_id': 1, 
        'title': '', 
        'first_name': '', 
        'last_name': '', 
        'reservation_id': 65
    }
    {'_state': <django.db.models.base.ModelState object at 0x000001C0C13DFA20>, 'id': 1, 'current_retail': Decimal('600.00'), 'service_class_id': 3, 'flight_id': 1}

    """
    # departure_flight_detail_staging = [
    #     {
    #         "passenger_id": passenger.id,
    #         "service_class": passenger.departure_flight_seat.service_class.name,
    #         "cabin_position"
    #
    #     }
    #     for passenger in queryresult_passenger
    # ]

    return_seats = None
    departure_seats = None
    print(request.GET['session_guid'])
    prompt()

    return render(request,'reservations/flight-confirmation.html')

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

    Only return flights that have seats available
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


