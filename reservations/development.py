from reservations.models_customers import *

# POST Body: <QueryDict: {'csrfmiddlewaretoken': ['NpLI10aXsyLsfjSlPOTDzWCRik6s88xiBRY5QL3a8QXpfhnbMhQlwIFZyTIHv8lO'], 'departure_airport': ['2'], 'arrival_airport': ['1'], 'departure_date': ['2020-05-23'], 'return_date': ['2020-05-24'], '
# number_of_passengers': ['2'], 'round_trip': ['on'], 'session_guid': ['647e6e3e-fd9f-4fe9-9015-db945e9fa4f8']}>

r = Reservation_Staging.objects.create(
    reservation = None,
    customer = 3,
    departure_airport = None,
    arrival_airport = None,
    departure_date = None,
    return_date = None,
    round_trip = None,
    session_guid = None
)