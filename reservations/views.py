from django.shortcuts import HttpResponse, render, reverse, HttpResponseRedirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login
from django.template import loader

import json
from datetime import date

from .models_customers import *


def searchFlightsHelper():
    print("Hello World!")


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


def chooseFlight(request):
    print('Request: ' + str(request.GET['flight_class']))
    template = loader.get_template('reservations/confirmation.html')
    context = {}
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

    Return results page back from search query

     - Generate SESSION GUID for current flight on the client side
     - Create SESSION object that is a subclass of the RESERVATION class
     - Return Flight Results page w/given Session ID as URL Parameter
     - If no 'return' path is specified then assume 'depart'
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


    if request.method == "POST":

        """
        REQUEST contains SESSION GUID that contains the state of the search criteria
        SESSION extends the RESERVATION object and the SESSION object merges with the RESERVATION object 
         when changes are finalized
        """
        flights = Flight.objects.filter(
            arrival_airport=request.POST['arrival_airport'],
            departure_airport=request.POST['departure_airport'],
            departure_datetime__date=request.POST['departure_date']
        )
        # print('FLIGHT OBJECT: ' + str(flights[0].__dict__))
        # print('Departure Airport: ' + str(flights[0].departure_airport.__dict__))
        # print('Flight: ' + str(flights[0].departure_airport.__dict__))
        template = loader.get_template('reservations/search-flights.html')
        context = {
            'flights': flights,
            'number_of_passengers': request.POST['number_of_passengers'],
            # 'round_trip': request.POST['round_trip'],
            'departure_date': request.POST['departure_date'],
            'return_date': request.POST['return_date'],
            'departure_airport': request.POST['departure_airport'],
            'arrival_airport': request.POST['arrival_airport']
        }
        # print(request.POST['session_guid'])
        # print('Flights object:  ' + str(flights[0].__dict__))
        return HttpResponseRedirect(template.render(context, request))
