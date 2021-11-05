from datetime import datetime, timezone

from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIRequestFactory
import restaurants.api.views
from restaurants.models import DietType, Diner, Restaurant, Table
from restaurants.models.reservation import Reservation


class CreateReservationTest(TestCase):
    endpoint_path = 'api/v1/reservations/'

    def setUp(self):
        self.factory = APIRequestFactory()
        self.view = restaurants.api.views.ReservationsView.as_view()

        # Diners
        self.diner_1 = Diner.objects.create(
            name='Maeby',
            house_location_lat=19.4349474,
            house_location_long=-99.1419256
        )

        self.diner_2 = Diner.objects.create(
            name='Tobias',
            house_location_lat=19.4384214,
            house_location_long=-99.2036906
        )

        # Restaurants
        self.restaurant_1 = Restaurant.objects.create(
            name='Panadería Rosetta',
            open_time='07:30:00',
            close_time='23:00:00',
            location_lat=23.530291579403467,
            location_long=-68.88613776794003
        )
        self.restaurant_1_table_1 = Table.objects.create(capacity=2, restaurant=self.restaurant_1)

        # Reservations
        self.restaurant_1_table_1_reservation_1 = Reservation(
            datetime=datetime(year=2100, month=11, day=3, hour=14, minute=0, tzinfo=timezone.utc),
            table=self.restaurant_1_table_1
        )
        self.restaurant_1_table_1_reservation_1.save()
        self.restaurant_1_table_1_reservation_1.diners.add(self.diner_1, self.diner_2)

    def test_delete_reservation(self):
        self.assertEqual(Reservation.objects.count(), 1)

        request = self.factory.delete("{}{}".format(self.endpoint_path, self.restaurant_1_table_1_reservation_1.id))
        resp = self.view(request, pk=self.restaurant_1_table_1_reservation_1.id)

        self.assertEqual(resp.status_code, 204)
        self.assertEqual(Reservation.objects.count(), 0)


