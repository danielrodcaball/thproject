from datetime import datetime, timezone
from django.test import TestCase
from rest_framework.test import APIRequestFactory
from restaurants.models import DietType, Diner, Restaurant, Table
import restaurants.services.restaurants_service
from restaurants.models.reservation import Reservation
import restaurants.api.views


class CreateReservationTest(TestCase):

    endpoint_path = 'api/v1/reservations/'

    def setUp(self):
        self.factory = APIRequestFactory()
        self.view = restaurants.api.views.ReservationsView.as_view()

        # Diet types
        vegan_diet_type = DietType.objects.create(name='Vegan')
        paleo_diet_type = DietType.objects.create(name='Paleo')

        # Diners
        self.diner_1 = Diner.objects.create(
            name='Maeby',
            house_location_lat=19.4349474,
            house_location_long=-99.1419256
        )
        self.diner_1.diet_types.add(vegan_diet_type)

        self.diner_2 = Diner.objects.create(
            name='Tobias',
            house_location_lat=19.4384214,
            house_location_long=-99.2036906
        )

        self.diner_3 = Diner.objects.create(
            name='Gob',
            house_location_lat=19.3318331,
            house_location_long=-99.2078983
        )

        self.diner_4 = Diner.objects.create(
            name='Lucile',
            house_location_lat=19.3634215,
            house_location_long=-99.1769323
        )

        self.diner_5 = Diner.objects.create(
            name='George Michael',
            house_location_lat=19.4058242,
            house_location_long=-99.1671942
        )
        self.diner_5.diet_types.add(paleo_diet_type)

        # Restaurants
        self.restaurant_1 = Restaurant.objects.create(
            name='Panadería Rosetta',
            open_time='07:30:00',
            close_time='23:00:00',
            location_lat=23.530291579403467,
            location_long=-68.88613776794003
        )
        self.restaurant_1.diet_endorsement_types.add(vegan_diet_type)
        self.restaurant_1_table_1 = Table.objects.create(capacity=2, restaurant=self.restaurant_1)

        self.restaurant_2 = Restaurant.objects.create(
            name='Lardo',
            open_time='08:00:00',
            close_time='23:00:00',
            location_lat=23.93258423336848,
            location_long=-60.36074714271186
        )
        self.restaurant_2.diet_endorsement_types.add(vegan_diet_type)
        self.restaurant_2_table_2 = Table.objects.create(capacity=4, restaurant=self.restaurant_2)

        self.restaurant_3 = Restaurant.objects.create(
            name='Paleo',
            open_time='14:00:00',
            close_time='23:59:00',
            location_lat=19.247787407295091,
            location_long=-99.14706284469599
        )
        self.restaurant_3.diet_endorsement_types.add(paleo_diet_type, vegan_diet_type)
        self.restaurant_3_table_1 = Table.objects.create(capacity=6, restaurant=self.restaurant_3)

        # Reservations
        restaurant_1_table_1_reservation_1 = Reservation(
            datetime=datetime(year=2100, month=11, day=3, hour=14, minute=0, tzinfo=timezone.utc),
            table=self.restaurant_1_table_1
        )
        restaurant_1_table_1_reservation_1.save()
        restaurant_1_table_1_reservation_1.diners.add(self.diner_1, self.diner_2)

    def test_cannot_create_reservation_for_a_past_date(self):
        target_datetime_str = '2020-11-03 14:30:00+00:00'

        post_request_data = {
            'diners': [self.diner_1.id],
            'target_datetime': target_datetime_str,
            'table': self.restaurant_2_table_2.id
        }

        request = self.factory.post(self.endpoint_path, post_request_data, format='json')
        resp = self.view(request)

        expected_resp = {
            "errors": {
                "display_error": "It is not possible to create a reservation for a past time ({})".format(
                    target_datetime_str),
                "internal_error_code": "40902"
            }
        }

        self.assertEqual(409, resp.status_code)
        self.assertEqual(expected_resp, resp.data)
        self.assertEqual(1, Reservation.objects.count())

    def test_cannot_create_reservation_for_a_table_without_capacity(self):
        diners = [self.diner_1.id, self.diner_2.id, self.diner_3.id, self.diner_4.id, self.diner_5.id]
        post_request_data = {
            'diners': diners,
            'target_datetime': '2100-11-03 14:30:00',
            'table': self.restaurant_2_table_2.id
        }

        request = self.factory.post(self.endpoint_path, post_request_data, format='json')
        resp = self.view(request)

        expected_resp = {
            "errors": {
                "display_error": "The selected table (capacity for {}) can not hold the amount of diners ({})".format(
                    self.restaurant_2_table_2.capacity, len(diners)),
                "internal_error_code": "40903"
            }
        }

        self.assertEqual(409, resp.status_code)
        self.assertEqual(expected_resp, resp.data)
        self.assertEqual(1, Reservation.objects.count())

    def test_cannot_create_reservation_to_an_occupied_table(self):
        target_datetime = '2100-11-03 14:30:00+00:00'
        post_request_data = {
            'diners': [self.diner_3.id, self.diner_4.id],
            'target_datetime': target_datetime,
            'table': self.restaurant_1_table_1.id
        }

        request = self.factory.post(self.endpoint_path, post_request_data, format='json')
        resp = self.view(request)

        expected_resp = {
            'errors': {
                'display_error': 'The selected table is occupied on the selected datetime ({})'.format(target_datetime),
                'internal_error_code': '40904'
            }
        }

        self.assertEqual(409, resp.status_code)
        self.assertEqual(expected_resp, resp.data)
        self.assertEqual(1, Reservation.objects.count())

    def test_cannot_create_reservation_to_a_diner_with_an_overlapping_reservation(self):
        post_request_data = {
            'diners': [self.diner_1.id],
            'target_datetime': '2100-11-03 14:30:00',
            'table': self.restaurant_2_table_2.id
        }

        request = self.factory.post(self.endpoint_path, post_request_data, format='json')
        resp = self.view(request)

        expected_resp = {
            'errors': {
                'display_error': 'Diner with id {id} has an overlapping reservation'.format(id=self.diner_1.id),
                'internal_error_code': '40901'
            }
        }

        self.assertEqual(409, resp.status_code)
        self.assertEqual(expected_resp, resp.data)
        self.assertEqual(1, Reservation.objects.count())

    def test_cannot_create_reservation_for_restaurant_that_doesnt_match_all_diet_restrictions(self):
        post_request_data = {
            'diners': [self.diner_5.id],
            'target_datetime': '2100-11-03 14:30:00',
            'table': self.restaurant_2_table_2.id
        }

        request = self.factory.post(self.endpoint_path, post_request_data, format='json')
        resp = self.view(request)

        expected_resp = {
            "errors": {
                "display_error": "The restaurant doesn't match all diners diet restrictions",
                "internal_error_code": "40905"
            }
        }

        self.assertEqual(409, resp.status_code)
        self.assertEqual(expected_resp, resp.data)
        self.assertEqual(1, Reservation.objects.count())

    def test_create_reservation_successfully(self):
        diners = [self.diner_1.id, self.diner_5.id]
        target_datetime = '2100-11-20 17:00:00Z'
        target_datetime_resp = '2100-11-20T17:00:00Z'
        post_request_data = {
            'diners': diners,
            'target_datetime': target_datetime,
            'table': self.restaurant_3_table_1.id
        }

        self.assertEqual(1, Reservation.objects.count())

        request = self.factory.post(self.endpoint_path, post_request_data, format='json')
        resp = self.view(request)

        self.assertEqual(2, Reservation.objects.count())
        self.assertTrue(set(resp.data['diners']) == set(diners))
        self.assertEqual(resp.data['table'], self.restaurant_3_table_1.id)
        self.assertEqual(resp.data['datetime'], target_datetime_resp)

        new_res = Reservation.objects.get(id=resp.data['id'])
        self.assertTrue(set(new_res.diners.values_list('id', flat=True)) == set(diners))
        self.assertEqual(new_res.table_id, self.restaurant_3_table_1.id)
        self.assertEqual(new_res.datetime.strftime('%Y-%m-%d %H:%M:%SZ'), target_datetime)


