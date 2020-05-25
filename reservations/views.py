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
    return render(request,"reservations/index.html")

def userCreation(request):
    if request.method == "GET":
        return render(request,"reservations/create-account.html")
    if request.method == "POST":
        customer = Customer.objects.create_user(
            username = request.POST['username'],
            email = request.POST['email_address'],
            password = request.POST['password'],
            first_name = request.POST['first_name'],
            last_name = request.POST['last_name']
        )
        login(request,customer)
        return HttpResponseRedirect(reverse('reservations:index'))

def userLogin(request):
    if request.method=="GET":
        return render(request,"reservations/sign-in.html")
    if request.method=="POST":
        customer = authenticate(
            request
            , username=request.POST['username']
            , password=request.POST['password']
        )
        login(request, customer)
        return HttpResponseRedirect(reverse('reservations:index'))

def bookReservation(request):
    if request.method=="GET":
        return render(request,"reservations/book.html")

def searchFlights(request):
    '''
    Return results page back from search query
    '''
    if request.method=="GET":
        flights = Flight.objects.filter(
            arrival_airport = request.GET['arrival_airport'],
            departure_airport = request.GET['departure_airport'],
            departure_datetime__date = request.GET['departure_date']
        )
        # print('FLIGHT OBJECT: ' + str(flights[0].__dict__))
        print('Departure Airport: ' + str(flights[0].departure_airport.__dict__))
        print('Flight: ' + str(flights[0].__dict__))
        template = loader.get_template('reservations/search-flights.html')
        context = {
            'flights':flights
        }
        return HttpResponse(template.render(context,request))
