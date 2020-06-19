from django.shortcuts import HttpResponse, render, reverse, HttpResponseRedirect
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
#     template = loader.get_template('reservations/choose-flight.html')
#     context = {'session_guid':request.GET['session_guid']}
#     return HttpResponse(template.render(context, request))

def submitFlightChoice(request):
    """
    Reservation --> Passenger --> PassengerSeat --> PlaneSeat
    """
    reservationSession = ReservationSession.objects.get(session_guid=request.POST['session_guid'])

    """
       <QueryDict: {'csrfmiddlewaretoken': ['CraBFMu1EwH6cG14J6nzmEv1ZlyO44rkQsQHncbSqaFfvFxCcBQQSfOUWBpQKfYP'], 'flight_class': ['{"flight_id":"1","class_id":"1"}']
       , 'number_of_passengers': ['2'], 'round_trip': ['on'], 'return_date': ['May 24, 2020'], 'arrival_airport': ['Airport object (1)'], 'session_guid': ['b111ee78-
       6d18-4645-823b-15083bc62690']}>
    """

    print(str(request.POST))
    prompt()

    # if staged reservation hasn't been created for session
    # create reservation staging object and link to current session
    """
    reservation_staging = ReservationSession.objects.create(
        customer = request.user,
        departure_flight = request.POST['flight_class'],
        return_flight = json.loads(request.POST['flight_class']).flight_id,
        number_of_passengers = reservationSession.number_of_passengers,
        round_trip = reservationSession.round_trip
    )
    """

    # else
    # update existing staged reservation
    """
    r = reservation_staging.objects.get(session_guid = ...)
    r.field_a = 
    r.field_b = 
    r.field_c = 
    r.save()    
    """

    # create passenger objects tied to object
    # assign passenger objects to 'reservation seat'
    # assign 'reservation seat' objects to 'plane seat'

    # to research: how to get all the passengers associated with a given reservation?


    if reservationSession.round_trip == "on":
        #redirect to departure flight page
        return HttpResponse('Select Departure Flight')
    else:
        #redirect to flight confirmation page
        return HttpResponse('Submit Flight Choice Page')

def reservationConfirmation(request):
    pass

def reservationCheckout(request):
    pass

def reservationFinalConfirmation(request):
    pass



def chooseFlight(request):
    #get reservation_staging object

    reservation_staging = ReservationSession.objects.get(session_guid=request.GET['session_guid'])

    #get flights that match the reservation_staging search criteria
    flights = Flight.objects.filter(
        arrival_airport=reservation_staging.arrival_airport,
        departure_airport=reservation_staging.departure_airport,
        departure_datetime__date=reservation_staging.departure_date
    )

    template = loader.get_template('reservations/choose-flight.html')
    context = {
        'flights': flights,
        'number_of_passengers': reservation_staging.number_of_passengers,
        'round_trip': reservation_staging.round_trip,
        'departure_date': reservation_staging.departure_date,
        'return_date': reservation_staging.return_date,
        'departure_airport':reservation_staging.departure_airport,
        'arrival_airport': reservation_staging.arrival_airport,
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
        ReservationSession.objects.create(
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

        #redirect user to search results page with SESSION GUID as URL parameter
        return HttpResponseRedirect(reverse('reservations:choose-flight') + '?session_guid=' + request.POST['session_guid'])


