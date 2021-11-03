import datetime
from django.db.models import QuerySet, Q, Subquery, F, Value, DateTimeField, ExpressionWrapper, Count
from django.db.models.functions import Sqrt, Power

from restaurants.models import Restaurant, Diner, DietType
from restaurants.models.reservation import Reservation

reservation_hours_span = 2


def find_restaurants(diners_ids=None, target_datetime: datetime.datetime = None, or_version=False) -> QuerySet:
    if diners_ids is None:
        diners_ids = []

    query = Q()

    # filtering by dietary restrictions
    if diners_ids:

        # if there are no restricted users they can go to any restaurant
        if not or_version:
            # AND VERSION:

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
            # OR VERSION:

            # removing diners without dietary restrictions, we only need the restricted ones, the others can go to any
            # restaurant
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
        end_target_datetime = target_datetime + datetime.timedelta(hours=reservation_hours_span)

        overlapping_reservations = Reservation.objects.annotate(
            end_datetime=ExpressionWrapper(
                F('datetime') + datetime.timedelta(hours=reservation_hours_span),
                output_field=DateTimeField()
            )
        ).filter(
            (Q(datetime__gte=target_datetime) & Q(datetime__lte=end_target_datetime)) |
            (Q(end_datetime__gte=target_datetime) & Q(end_datetime__lte=end_target_datetime))
        )

        restaurants_ids_qs = Restaurant.objects.filter(
            Q(table__capacity__gte=len(diners_ids)) &
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
