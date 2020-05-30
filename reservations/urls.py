from django.urls import path
from . import views

app_name = 'reservations'
urlpatterns = [
    path('', views.index, name='index'),
    path('create-account', views.userCreation, name ='create-account'),
    path('sign-in', views.userLogin, name ='sign-in'),
    path('book', views.bookReservation, name = 'book'),
    path('search-flights', views.searchFlights, name = 'search-flights'),
    path('confirmation', views.chooseFlight, name = 'confirmation')
]
