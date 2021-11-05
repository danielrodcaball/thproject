import datetime
from django.db.models import QuerySet, Q, Subquery, F, Value, DateTimeField, ExpressionWrapper, BooleanField
from django.db.models.functions import Sqrt, Power

from restaurants.api.serializers import FindRestaurantsValidator, ReservationSerializer
from restaurants.custom_errors import DinerWithOverlappingReservationError, ReservationForAPastTimeError, \
    TableCanNotHoldDinersQtyError, TableOccupiedError, RestaurantDoesntMatchAllDinersDietRestrictionsError
from restaurants.models import Restaurant, Diner, DietType
from restaurants.models.reservation import Reservation

_reservation_hours_span = 2


def create_reservation(diners: list, target_datetime: str, table: int):
    validator = ReservationSerializer(data={'diners': diners, 'table': table, 'datetime': target_datetime})
    validator.is_valid(raise_exception=True)

    diners_ids = diners
    diners = validator.validated_data['diners']
    table = validator.validated_data['table']
    target_datetime = validator.validated_data['datetime']

    end_target_datetime = target_datetime + datetime.timedelta(hours=_reservation_hours_span)

    # Validating that the reservation not for a past datetime
    if target_datetime < datetime.datetime.now(tz=datetime.timezone.utc):
        raise ReservationForAPastTimeError(target_datetime)

    # Validating the table can hold the amount of diners
    if table.capacity < len(diners):
        raise TableCanNotHoldDinersQtyError(table_capacity=table.capacity, diners_qty=len(diners))

    # Validating the table is not occupied on the selected datetime
    overlapping_reservations = Reservation.objects.annotate(
        end_datetime=ExpressionWrapper(
            F('datetime') + datetime.timedelta(hours=_reservation_hours_span),
            output_field=DateTimeField()
        )
    ).filter(
        Q(table_id=table.id) &
        (
                (Q(datetime__lte=target_datetime) & Q(end_datetime__gte=target_datetime)) |
                (Q(datetime__lte=end_target_datetime) & Q(end_datetime__gt=end_target_datetime))
        )
    )

    if overlapping_reservations.exists():
        raise TableOccupiedError(target_datetime=target_datetime)

    # Validating the restaurant match all diet restriction of all diners
    diners_diet_types_set = set(DietType.objects.filter(diner__in=diners_ids).distinct())
    restaurant_diet_types_set = set(DietType.objects.filter(restaurant=table.restaurant_id).distinct())

    # if the diners diet types is not a subset of the restaurant diet types then raise an exception
    if not diners_diet_types_set <= restaurant_diet_types_set:
        raise RestaurantDoesntMatchAllDinersDietRestrictionsError()

    # Validating that diners don't have overlapping reservations
    for diner in diners:
        overlapping_reservations_qs = Reservation.objects.annotate(
            end_datetime=ExpressionWrapper(
                F('datetime') + datetime.timedelta(hours=_reservation_hours_span),
                output_field=DateTimeField()
            )
        ).filter(
            Q(diners=diner) &
            (
                    (Q(datetime__lte=target_datetime) & Q(end_datetime__gte=target_datetime)) |
                    (Q(datetime__lte=end_target_datetime) & Q(end_datetime__gt=end_target_datetime))
            )
        )

        if overlapping_reservations_qs.exists():
            raise DinerWithOverlappingReservationError(diner_id=diner.id)

    # Saving reservation
    reservation = Reservation.objects.create(datetime=target_datetime, table_id=table.id)
    reservation.save()
    reservation.diners.add(*diners)
    return reservation


def find_restaurants(diners=None, target_datetime: str = None, or_version=False) -> QuerySet:
    if diners is None:
        diners = []

    validator = FindRestaurantsValidator(data={'diners': diners, 'target_datetime': target_datetime})
    validator.is_valid(raise_exception=True)

    diners_ids = diners
    # diners = validator.validated_data['diners']  # Diners objects, we dont need it in this service
    target_datetime = validator.validated_data['target_datetime']

    query = Q()

    # filtering by the restaurants that match the dietary restrictions. In the AND version every returned restaurant
    # must match all dietary restrictions of every user. In the OR version every restaurant must match at least one
    # dietary restriction of every user
    if diners_ids:

        if not or_version:
            # *************** AND VERSION ***************

            diet_types_ids = list(DietType.objects.filter(diner__in=diners_ids).values_list('id', flat=True).distinct())

            if len(diet_types_ids) > 0:

                restaurants_ids_qs = Restaurant.objects.filter(
                    diet_endorsement_types=diet_types_ids.pop()
                ).values('id').distinct()

                for diet_type_id in diet_types_ids:
                    restaurants_ids_qs = restaurants_ids_qs.intersection(
                        Restaurant.objects.filter(
                            diet_endorsement_types=diet_type_id
                        ).values('id').distinct()
                    )

                query &= Q(id__in=Subquery(restaurants_ids_qs))

        else:
            # *************** OR VERSION ***************

            # removing diners without dietary restrictions, we only need the restricted ones because the others can
            # go to any restaurant
            restricted_diners_ids = [diner_id for diner_id in diners_ids if
                                     DietType.objects.filter(diner=diner_id).count() > 0]

            if restricted_diners_ids:

                restaurants_ids_qs = Restaurant.objects.filter(
                    diet_endorsement_types__in=Subquery(
                        DietType.objects.filter(diner=restricted_diners_ids.pop()).values('id')
                    )
                ).values('id').distinct()

                for diner_id in restricted_diners_ids:
                    restaurants_ids_qs = restaurants_ids_qs.intersection(
                        Restaurant.objects.filter(
                            diet_endorsement_types__in=Subquery(DietType.objects.filter(diner=diner_id).values('id'))
                        ).values('id').distinct()
                    )

                query &= Q(id__in=Subquery(restaurants_ids_qs))

    # filtering by time availability
    if target_datetime:
        end_target_datetime = target_datetime + datetime.timedelta(hours=_reservation_hours_span)

        overlapping_reservations = Reservation.objects.annotate(
            end_datetime=ExpressionWrapper(
                F('datetime') + datetime.timedelta(hours=_reservation_hours_span),
                output_field=DateTimeField()
            )
        ).filter(
            (Q(datetime__gte=target_datetime) & Q(datetime__lte=end_target_datetime)) |
            (Q(end_datetime__gte=target_datetime) & Q(end_datetime__lte=end_target_datetime))
        )

        rn0 = target_datetime.time()  # reservation start time
        rn1 = end_target_datetime.time()  # reservation end time
        day_end_time = datetime.time(hour=23, minute=59, second=59, microsecond=999999)
        day_start_time = datetime.time(hour=0, minute=0, second=0, microsecond=0)

        restaurants_ids_qs = Restaurant.objects.filter(
            # Filtering by the restaurants with open hours in the time of the reservation
            ((
                     Q(open_time__lt=F('close_time')) &
                     (Q(open_time__lte=rn0) & Q(close_time__gte=rn0)) &
                     (Q(open_time__lte=rn1) & Q(close_time__gte=rn1))
             ) |
             (
                     Q(open_time__gt=F('close_time')) &
                     (
                             (Q(open_time__lte=rn0) & Q(
                                 ExpressionWrapper(Value(rn0 <= day_end_time), BooleanField()))) |
                             (Q(ExpressionWrapper(Value(rn0 >= day_start_time), BooleanField())) & Q(
                                 close_time__gte=rn0))
                     ) &
                     (
                             (Q(open_time__lte=rn1) & Q(
                                 ExpressionWrapper(Value(rn1 <= day_end_time), BooleanField()))) |
                             (Q(ExpressionWrapper(Value(rn1 >= day_start_time), BooleanField())) & Q(
                                 close_time__gte=rn1))
                     )
             )) &

            # Filtering by restaurant with tables capacity for the amount of diners
            Q(table__capacity__gte=len(diners_ids)) &

            # Filtering by restaurants with time availability
            ~Q(table__in=Subquery(overlapping_reservations.values('table_id').distinct()))

        ).values('id').distinct()

        query &= Q(id__in=Subquery(restaurants_ids_qs))

    restaurants_qs = Restaurant.objects.filter(query)

    # if there are diners then sort the restaurants by the total distance from diners to the restaurant
    if diners_ids:

        total_distance_expr = Value(0)

        for diner_id in diners_ids:
            diner = Diner.objects.get(id=diner_id)
            total_distance_expr += Sqrt(
                Power(diner.house_location_lat - F('location_lat'), 2) +
                Power(diner.house_location_long - F('location_long'), 2)
            )

        restaurants_qs = restaurants_qs.annotate(total_distance=total_distance_expr).order_by('total_distance')

    return restaurants_qs
