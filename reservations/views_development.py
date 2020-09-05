from .models_customers import *


def getAvailableFlightSeats(flight):
    reservations_queryresult = Reservation_Staging.objects.filter(departure_flight=flight)
    passengers_queryresult = Passenger_Staging.objects.filter(reservation__in=reservations_queryresult)
    flightseat_queryresult = PlaneSeat.objects \
        .filter(plane_model=flight.plane.plane_model) \
        .exclude(id__in=[passenger.departure_flight_seat_id for passenger in passengers_queryresult if
                         passenger.departure_flight_seat_id != None])

    return flightseat_queryresult

def getNextLowestServiceClass(current_service_class):
    current_level = current_service_class.level
    next_level = current_level - 1

    if next_level < 1:
        return None
    else:
        return ServiceClass.objects.get(level=next_level)

def test1():
    reservation_staging = Reservation_Staging.objects.get(id=5184)
    passenger_staging_queryresult = Passenger_Staging.objects.filter(reservation=reservation_staging)

    passenger = passenger_staging_queryresult[0]
    passenger_service_class = passenger.departure_flight_seat.service_class
    flightseat_queryresult = getAvailableFlightSeats(reservation_staging.departure_flight)
    available_seats_queryresult = flightseat_queryresult \
        .filter(service_class=passenger_service_class) \
        .order_by('serial_position')

    count_available_seats = available_seats_queryresult.count()

    if count_available_seats == 0:
        passenger_service_class = getNextLowestServiceClass(passenger_service_class)
        if passenger_service_class == None:
            print('Error')

    serviceClass = ServiceClass.objects.get(level=3)
    print(serviceClass.name)
    serviceClass = getNextLowestServiceClass(serviceClass)
    print(serviceClass.name)
    serviceClass = getNextLowestServiceClass(serviceClass)
    print(serviceClass.name)

    output = serviceClass.name

def test_logic():

    return output