from datetime import datetime, timezone

from django.test import TestCase
from restaurants.models import DietType, Diner, Restaurant, Table
import restaurants.services.reservations_service
from restaurants.models.reservation import Reservation


class FindRestaurantsTestOR(TestCase):
    def setUp(self):

        # Diet types
        vegan_diet_type = DietType.objects.create(name='Vegan')
        paleo_diet_type = DietType.objects.create(name='Paleo')
        gluten_free_diet_type = DietType.objects.create(name='Gluten-Free')
        vegetarian_diet_type = DietType.objects.create(name='Vegetarian')

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
        self.diner_3.diet_types.add(paleo_diet_type)

        self.diner_4 = Diner.objects.create(
            name='Lucile',
            house_location_lat=19.3634215,
            house_location_long=-99.1769323
        )
        self.diner_4.diet_types.add(gluten_free_diet_type)

        self.diner_5 = Diner.objects.create(
            name='George Michael',
            house_location_lat=19.4058242,
            house_location_long=-99.1671942
        )
        self.diner_5.diet_types.add(vegetarian_diet_type, gluten_free_diet_type)

        self.diner_6 = Diner.objects.create(
            name='Michael',
            house_location_lat=19.4153107,
            house_location_long=-99.1804722
        )
        self.diner_6.diet_types.add(vegetarian_diet_type)

        self.diner_7 = Diner.objects.create(
            name='Daniel',
            house_location_lat=19.4153107,
            house_location_long=-99.1804722
        )

        # Restaurants with tables
        self.restaurant_1 = Restaurant.objects.create(
            name='Panadería Rosetta',
            location_lat=23.530291579403467,
            location_long=-68.88613776794003
        )
        self.restaurant_1.diet_endorsement_types.add(vegan_diet_type, vegetarian_diet_type)
        self.restaurant_1_table_1 = Table.objects.create(capacity=2, restaurant=self.restaurant_1)
        self.restaurant_1_table_2 = Table.objects.create(capacity=4, restaurant=self.restaurant_1)
        self.restaurant_1_table_3 = Table.objects.create(capacity=6, restaurant=self.restaurant_1)


        self.restaurant_2 = Restaurant.objects.create(
            name='Lardo',
            location_lat=23.93258423336848,
            location_long=-60.36074714271186
        )
        self.restaurant_2.diet_endorsement_types.add(gluten_free_diet_type)
        self.restaurant_2_table_1 = Table.objects.create(capacity=2, restaurant=self.restaurant_2)
        self.restaurant_2_table_2 = Table.objects.create(capacity=4, restaurant=self.restaurant_2)
        self.restaurant_2_table_3 = Table.objects.create(capacity=6, restaurant=self.restaurant_2)

        self.restaurant_3 = Restaurant.objects.create(
            name='Falling Piano Brewing Co',
            location_lat=23.887821602907994,
            location_long=-79.8098463664155
        )
        self.restaurant_3.diet_endorsement_types.add(vegetarian_diet_type)
        self.restaurant_3_table_1 = Table.objects.create(capacity=2, restaurant=self.restaurant_3)
        self.restaurant_3_table_2 = Table.objects.create(capacity=4, restaurant=self.restaurant_3)
        self.restaurant_3_table_3 = Table.objects.create(capacity=6, restaurant=self.restaurant_3)

        self.restaurant_4 = Restaurant.objects.create(
            name='Paleo',
            location_lat=19.247787407295091,
            location_long=-99.14706284469599
        )
        self.restaurant_4.diet_endorsement_types.add(paleo_diet_type)
        self.restaurant_4_table_1 = Table.objects.create(capacity=2, restaurant=self.restaurant_4)
        self.restaurant_4_table_2 = Table.objects.create(capacity=4, restaurant=self.restaurant_4)
        self.restaurant_4_table_3 = Table.objects.create(capacity=6, restaurant=self.restaurant_4)

        self.restaurant_5 = Restaurant.objects.create(
            name='No endorsement',
            location_lat=19.247787407295091,
            location_long=-99.14706284469599
        )
        self.restaurant_5_table_1 = Table.objects.create(capacity=2, restaurant=self.restaurant_5)
        self.restaurant_5_table_2 = Table.objects.create(capacity=4, restaurant=self.restaurant_5)
        self.restaurant_5_table_3 = Table.objects.create(capacity=6, restaurant=self.restaurant_5)

        self.restaurant_6 = Restaurant.objects.create(
            name='Gluten and Vegan',
            location_lat=22.803066749076024,
            location_long=-38.21230964211913
        )
        self.restaurant_6.diet_endorsement_types.add(gluten_free_diet_type, vegan_diet_type)
        self.restaurant_6_table_1 = Table.objects.create(capacity=4, restaurant=self.restaurant_6)
        self.restaurant_6_table_2 = Table.objects.create(capacity=2, restaurant=self.restaurant_6)
        # self.restaurant_6_table_3 = Table.objects.create(capacity=6, restaurant=self.restaurant_6)

        # Reservations
        restaurant_6_table_1_reservation_1 = Reservation(
            datetime=datetime(year=2021, month=11, day=3, hour=21, minute=0, tzinfo=timezone.utc),
            table=self.restaurant_6_table_1
        )
        restaurant_6_table_1_reservation_1.save()
        restaurant_6_table_1_reservation_1.diners.add(self.diner_1, self.diner_2)

    def test_find_restaurants_without_diners_and_without_datetime(self):
        restaurants_qs = restaurants.services.reservations_service.find_restaurants(or_version=True)
        self.assertEqual(restaurants_qs.count(), 6)

    def test_find_restaurants_vegetarian_or_gluten(self):
        # looking for: vegetarian OR gluten
        diners = [self.diner_5.id, self.diner_2.id]
        restaurants_qs = restaurants.services.reservations_service.find_restaurants(diners_ids=diners, or_version=True)
        restaurants_ids = restaurants_qs.values_list('id', flat=True)
        self.assertEqual(restaurants_qs.count(), 4)
        self.assertTrue(self.restaurant_1.id in restaurants_ids)
        self.assertTrue(self.restaurant_2.id in restaurants_ids)
        self.assertTrue(self.restaurant_3.id in restaurants_ids)
        self.assertTrue(self.restaurant_6.id in restaurants_ids)

    def test_find_restaurants_vegetarian_or_gluten_and_vegetarian_and_vegan(self):
        # looking for: (vegetarian OR gluten) AND vegetarian AND vegan
        diners = [self.diner_5.id, self.diner_6.id, self.diner_2.id, self.diner_1.id]
        restaurants_qs = restaurants.services.reservations_service.find_restaurants(diners_ids=diners, or_version=True)
        restaurants_ids = restaurants_qs.values_list('id', flat=True)
        self.assertEqual(restaurants_qs.count(), 1)
        self.assertTrue(self.restaurant_1.id in restaurants_ids)

    def test_find_restaurants_vegetarian_or_gluten_and_paleo(self):
        # looking for: (vegetarian OR gluten) AND paleo
        diners = [self.diner_5.id, self.diner_2.id, self.diner_3.id]
        restaurants_qs = restaurants.services.reservations_service.find_restaurants(diners_ids=diners, or_version=True)
        self.assertEqual(restaurants_qs.count(), 0)

    def test_find_restaurants_order(self):
        diners = [self.diner_5.id, self.diner_2.id]
        restaurants_qs = restaurants.services.reservations_service.find_restaurants(diners_ids=diners, or_version=True)
        self.assertEqual(restaurants_qs.count(), 4)
        self.assertEqual(restaurants_qs[0].id, self.restaurant_3.id)
        self.assertEqual(restaurants_qs[1].id, self.restaurant_1.id)
        self.assertEqual(restaurants_qs[2].id, self.restaurant_2.id)
        self.assertEqual(restaurants_qs[3].id, self.restaurant_6.id)

    def test_find_restaurants_diet_restrictions_order_and_availability(self):
        diners = [self.diner_5.id, self.diner_2.id, self.diner_7.id]

        # looking for: vegetarian OR gluten with a table for two at 2021-11-01 21:00:00
        restaurants_qs = restaurants.services.reservations_service.find_restaurants(
            diners_ids=diners,
            target_datetime=datetime(year=2021, month=11, day=3, hour=21, minute=0, tzinfo=timezone.utc),
            or_version=True
        )

        self.assertEqual(restaurants_qs.count(), 2)
        self.assertEqual(restaurants_qs[0].id, self.restaurant_3.id)
        self.assertEqual(restaurants_qs[1].id, self.restaurant_2.id)

        restaurants_qs = restaurants.services.reservations_service.find_restaurants(
            diners_ids=diners,
            target_datetime=datetime(year=2021, month=11, day=3, hour=21, minute=30, tzinfo=timezone.utc),
            or_version=True
        )

        self.assertEqual(restaurants_qs.count(), 1)
        self.assertEqual(restaurants_qs[0].id, self.restaurant_3.id)

        restaurants_qs = restaurants.services.reservations_service.find_restaurants(
            diners_ids=diners,
            target_datetime=datetime(year=2021, month=11, day=3, hour=20, minute=30, tzinfo=timezone.utc),
            or_version=True
        )

        self.assertEqual(restaurants_qs.count(), 2)
        self.assertEqual(restaurants_qs[0].id, self.restaurant_3.id)
        self.assertEqual(restaurants_qs[1].id, self.restaurant_2.id)

        restaurants_qs = restaurants.services.reservations_service.find_restaurants(
            diners_ids=diners,
            target_datetime=datetime(year=2021, month=11, day=3, hour=19, minute=00, tzinfo=timezone.utc),
            or_version=True
        )

        self.assertEqual(restaurants_qs.count(), 3)
        self.assertEqual(restaurants_qs[0].id, self.restaurant_3.id)
        self.assertEqual(restaurants_qs[1].id, self.restaurant_1.id)
        self.assertEqual(restaurants_qs[2].id, self.restaurant_2.id)

        restaurants_qs = restaurants.services.reservations_service.find_restaurants(
            diners_ids=diners,
            target_datetime=datetime(year=2021, month=11, day=3, hour=15, minute=59, tzinfo=timezone.utc),
            or_version=True
        )

        self.assertEqual(restaurants_qs.count(), 4)
        self.assertEqual(restaurants_qs[0].id, self.restaurant_3.id)
        self.assertEqual(restaurants_qs[1].id, self.restaurant_1.id)
        self.assertEqual(restaurants_qs[2].id, self.restaurant_2.id)
        self.assertEqual(restaurants_qs[3].id, self.restaurant_6.id)

        diners = [self.diner_5.id, self.diner_2.id]
        restaurants_qs = restaurants.services.reservations_service.find_restaurants(
            diners_ids=diners,
            target_datetime=datetime(year=2021, month=11, day=3, hour=21, minute=0, tzinfo=timezone.utc),
            or_version=True
        )
        self.assertEqual(restaurants_qs.count(), 3)
        self.assertEqual(restaurants_qs[0].id, self.restaurant_3.id)
        self.assertEqual(restaurants_qs[1].id, self.restaurant_2.id)
        self.assertEqual(restaurants_qs[2].id, self.restaurant_6.id)


class FindRestaurantsTestAND(TestCase):
    def setUp(self):
        # Diet types
        vegan_diet_type = DietType.objects.create(name='Vegan')
        paleo_diet_type = DietType.objects.create(name='Paleo')
        gluten_free_diet_type = DietType.objects.create(name='Gluten-Free')
        vegetarian_diet_type = DietType.objects.create(name='Vegetarian')

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
        self.diner_3.diet_types.add(paleo_diet_type)

        self.diner_4 = Diner.objects.create(
            name='Lucile',
            house_location_lat=19.3634215,
            house_location_long=-99.1769323
        )
        self.diner_4.diet_types.add(gluten_free_diet_type)

        self.diner_5 = Diner.objects.create(
            name='George Michael',
            house_location_lat=19.4058242,
            house_location_long=-99.1671942
        )
        self.diner_5.diet_types.add(vegetarian_diet_type, gluten_free_diet_type)

        self.diner_6 = Diner.objects.create(
            name='Michael',
            house_location_lat=19.4153107,
            house_location_long=-99.1804722
        )
        self.diner_6.diet_types.add(vegetarian_diet_type)

        self.diner_7 = Diner.objects.create(
            name='Daniel',
            house_location_lat=19.4153107,
            house_location_long=-99.1804722
        )

        # Restaurants with tables
        self.restaurant_1 = Restaurant.objects.create(
            name='Panadería Rosetta',
            location_lat=23.530291579403467,
            location_long=-68.88613776794003
        )
        self.restaurant_1.diet_endorsement_types.add(gluten_free_diet_type, vegetarian_diet_type)
        self.restaurant_1_table_1 = Table.objects.create(capacity=2, restaurant=self.restaurant_1)
        self.restaurant_1_table_2 = Table.objects.create(capacity=4, restaurant=self.restaurant_1)
        self.restaurant_1_table_3 = Table.objects.create(capacity=6, restaurant=self.restaurant_1)

        self.restaurant_2 = Restaurant.objects.create(
            name='Lardo',
            location_lat=23.93258423336848,
            location_long=-60.36074714271186
        )
        self.restaurant_2.diet_endorsement_types.add(gluten_free_diet_type)
        self.restaurant_2_table_1 = Table.objects.create(capacity=2, restaurant=self.restaurant_2)
        self.restaurant_2_table_2 = Table.objects.create(capacity=4, restaurant=self.restaurant_2)
        self.restaurant_2_table_3 = Table.objects.create(capacity=6, restaurant=self.restaurant_2)

        self.restaurant_3 = Restaurant.objects.create(
            name='Falling Piano Brewing Co',
            location_lat=23.887821602907994,
            location_long=-79.8098463664155
        )
        self.restaurant_3.diet_endorsement_types.add(vegetarian_diet_type, gluten_free_diet_type)
        self.restaurant_3_table_1 = Table.objects.create(capacity=2, restaurant=self.restaurant_3)
        self.restaurant_3_table_2 = Table.objects.create(capacity=4, restaurant=self.restaurant_3)
        self.restaurant_3_table_3 = Table.objects.create(capacity=6, restaurant=self.restaurant_3)

        self.restaurant_4 = Restaurant.objects.create(
            name='Paleo',
            location_lat=19.247787407295091,
            location_long=-99.14706284469599
        )
        self.restaurant_4.diet_endorsement_types.add(paleo_diet_type)
        self.restaurant_4_table_1 = Table.objects.create(capacity=2, restaurant=self.restaurant_4)
        self.restaurant_4_table_2 = Table.objects.create(capacity=4, restaurant=self.restaurant_4)
        self.restaurant_4_table_3 = Table.objects.create(capacity=6, restaurant=self.restaurant_4)

        self.restaurant_5 = Restaurant.objects.create(
            name='No endorsement',
            location_lat=19.247787407295091,
            location_long=-99.14706284469599
        )
        self.restaurant_5_table_1 = Table.objects.create(capacity=2, restaurant=self.restaurant_5)
        self.restaurant_5_table_2 = Table.objects.create(capacity=4, restaurant=self.restaurant_5)
        self.restaurant_5_table_3 = Table.objects.create(capacity=6, restaurant=self.restaurant_5)

        self.restaurant_6 = Restaurant.objects.create(
            name='Gluten and Vegan',
            location_lat=22.803066749076024,
            location_long=-38.21230964211913
        )
        self.restaurant_6.diet_endorsement_types.add(gluten_free_diet_type, vegetarian_diet_type, paleo_diet_type)
        self.restaurant_6_table_1 = Table.objects.create(capacity=4, restaurant=self.restaurant_6)
        self.restaurant_6_table_2 = Table.objects.create(capacity=2, restaurant=self.restaurant_6)
        # self.restaurant_6_table_3 = Table.objects.create(capacity=6, restaurant=self.restaurant_6)

        # Reservations
        restaurant_6_table_1_reservation_1 = Reservation(
            datetime=datetime(year=2021, month=11, day=3, hour=14, minute=0, tzinfo=timezone.utc),
            table=self.restaurant_6_table_1
        )
        restaurant_6_table_1_reservation_1.save()
        restaurant_6_table_1_reservation_1.diners.add(self.diner_1, self.diner_2)

    def test_find_restaurants(self):
        restaurants_qs = restaurants.services.reservations_service.find_restaurants()
        self.assertEqual(restaurants_qs.count(), 6)

        restaurants_qs = restaurants.services.reservations_service.find_restaurants(diners_ids=[self.diner_2.id])
        self.assertEqual(restaurants_qs.count(), 6)

        restaurants_qs = restaurants.services.reservations_service.find_restaurants(diners_ids=[self.diner_5.id, self.diner_2.id, self.diner_6.id])
        self.assertEqual(restaurants_qs.count(), 3)
        self.assertEqual(restaurants_qs[0].id, self.restaurant_3.id)
        self.assertEqual(restaurants_qs[1].id, self.restaurant_1.id)
        self.assertEqual(restaurants_qs[2].id, self.restaurant_6.id)

        restaurants_qs = restaurants.services.reservations_service.find_restaurants(diners_ids=[self.diner_5.id, self.diner_2.id, self.diner_6.id, self.diner_3.id])
        self.assertEqual(restaurants_qs.count(), 1)
        self.assertEqual(restaurants_qs[0].id, self.restaurant_6.id)

        # Testing reservations

        # Occupied
        restaurants_qs = restaurants.services.reservations_service.find_restaurants(
            diners_ids=[self.diner_5.id, self.diner_2.id, self.diner_6.id, self.diner_3.id],
            target_datetime=datetime(year=2021, month=11, day=3, hour=14, minute=0, tzinfo=timezone.utc)
        )
        self.assertEqual(restaurants_qs.count(), 0)

        restaurants_qs = restaurants.services.reservations_service.find_restaurants(
            diners_ids=[self.diner_5.id, self.diner_2.id, self.diner_6.id, self.diner_3.id],
            target_datetime=datetime(year=2021, month=11, day=3, hour=16, minute=0, tzinfo=timezone.utc)
        )
        self.assertEqual(restaurants_qs.count(), 0)

        restaurants_qs = restaurants.services.reservations_service.find_restaurants(
            diners_ids=[self.diner_5.id, self.diner_2.id, self.diner_6.id, self.diner_3.id],
            target_datetime=datetime(year=2021, month=11, day=3, hour=12, minute=0, tzinfo=timezone.utc)
        )
        self.assertEqual(restaurants_qs.count(), 0)

        # Free
        restaurants_qs = restaurants.services.reservations_service.find_restaurants(
            diners_ids=[self.diner_5.id, self.diner_2.id, self.diner_6.id, self.diner_3.id],
            target_datetime=datetime(year=2021, month=11, day=3, hour=11, minute=59, tzinfo=timezone.utc)
        )
        self.assertEqual(restaurants_qs.count(), 1)
        self.assertEqual(restaurants_qs[0].id, self.restaurant_6.id)

        restaurants_qs = restaurants.services.reservations_service.find_restaurants(
            diners_ids=[self.diner_5.id, self.diner_3.id],
            target_datetime=datetime(year=2021, month=11, day=3, hour=14, minute=00, tzinfo=timezone.utc)
        )
        self.assertEqual(restaurants_qs.count(), 1)
        self.assertEqual(restaurants_qs[0].id, self.restaurant_6.id)
