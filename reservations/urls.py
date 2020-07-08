from django.urls import path
from . import views

app_name = 'reservations'
urlpatterns = [
    path('', views.index, name='index'),
    path('create-account', views.userCreation, name ='create-account'),
    path('sign-in', views.userLogin, name ='sign-in'),
    path('book', views.bookReservation, name = 'book'),
    path('search-flights', views.searchFlights, name = 'search-flights'),
    path('choose-flight/departure', views.chooseDepartureFlight, name='choose-departure-flight'),
    path('choose-flight/return', views.chooseReturnFlight, name='choose-return-flight'),
    path('reservation-confirmation', views.chooseDepartureFlight, name ='reservation-confirmation'),
    path('submit-departure-flight-choice', views.submitDepartureFlightChoice, name ='submit-departure-flight-choice'),
    path('submit-return-flight-choice', views.submitReturnFlightChoice, name ='submit-return-flight-choice'),
    path('flight-confirmation', views.flightConfirmation, name='flight-confirmation')
]
