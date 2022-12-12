from django.test import TestCase, Client
from django.db.models import Max

from . import models


class FlightTestCase(TestCase):

    def setUp(self):
        # create airports
        a1 = models.Airport.objects.create(code="AAA", city="City A")
        a2 = models.Airport.objects.create(code="BBB", city="City B")

        # create flights
        models.Flight.objects.create(origin=a1, destination=a2, duration=100)
        models.Flight.objects.create(origin=a1, destination=a1, duration=200)
        models.Flight.objects.create(origin=a1, destination=a2, duration=-100)

    def test_departures_count(self):
        a = models.Airport.objects.get(code="AAA")
        self.assertEqual(a.departures.count(), 3)

    def test_arrival_count(self):
        a = models.Airport.objects.get(code="AAA")
        self.assertEqual(a.arrivals.count(), 1)

    def test_valid_flight(self):
        a1 = models.Airport.objects.get(code="AAA")
        a2 = models.Airport.objects.get(code="BBB")
        f = models.Flight.objects.get(origin=a1, destination=a2, duration=100)
        self.assertTrue(f.is_valid_flight())

    def test_invalid_flight_destination(self):
        a1 = models.Airport.objects.get(code="AAA")
        f = models.Flight.objects.get(origin=a1, destination=a1)
        self.assertFalse(f.is_valid_flight())

    def test_invalid_flight_duration(self):
        a1 = models.Airport.objects.get(code="AAA")
        a2 = models.Airport.objects.get(code="BBB")
        f = models.Flight.objects.get(origin=a1, destination=a2, duration=-100)
        self.assertFalse(f.is_valid_flight())

    def test_index(self):
        c = Client()
        response = c.get("/flights/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["flights"].count(), 3)  # in the setUp above, 3 flight was created

    def test_valid_flight_page(self):
        a1 = models.Airport.objects.get(code="AAA")
        f = models.Flight.objects.get(origin=a1, destination=a1)

        c = Client()
        response = c.get(f"/flights/{f.id}")
        self.assertEqual(response.status_code, 200)

    def test_invalid_flight_page(self):
        max_id = models.Flight.objects.all().aggregate(Max("id"))["id__max"]

        c = Client()
        response = c.get(f"/flights/{max_id + 1}")
        self.assertEqual(response.status_code, 404)

    def test_flight_page_passengers(self):
        f = models.Flight.objects.get(pk=1)
        p = models.Passenger.objects.create(first="Alice", last="Adams")
        f.passengers.add(p)

        c = Client()
        response = c.get(f"/flights/{f.id}")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["passengers"].count(), 1)

    def test_flight_page_non_passengers(self):
        f = models.Flight.objects.get(pk=1)
        p = models.Passenger.objects.create(first="Alice", last="Adams")

        c = Client()
        response = c.get(f"/flights/{f.id}")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["non_passengers"].count(), 1)
