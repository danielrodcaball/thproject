from rest_framework import status
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

import restaurants.services.restaurants_service
import rest_framework.exceptions
from rest_framework.pagination import PageNumberPagination

from restaurants import custom_errors
from restaurants.api.serializers import RestaurantSerializer, ReservationSerializer
from restaurants.models.reservation import Reservation


def get_validation_error_response(validation_error: rest_framework.exceptions.ValidationError, http_status_code: int):
    response = {
        'errors': {
            'display_error': 'Validation Error',
            'field_errors': validation_error.detail
        }
    }
    return Response(response, status=http_status_code)


def get_business_requirement_error_response(business_logic_error: custom_errors.BusinessError, http_status_code):
    response = {
        'errors': {
            'display_error': business_logic_error.message,
            'internal_error_code': business_logic_error.error_code
        }
    }
    return Response(response, status=http_status_code)


class RestaurantsView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):

        diners_ids = self.request.query_params.getlist('diners', default=None)
        target_datetime_str = self.request.query_params.get('target_datetime', default=None)

        try:
            restaurants_qs = restaurants.services.restaurants_service.find_restaurants(
                diners=diners_ids,
                target_datetime=target_datetime_str
            )
        except rest_framework.exceptions.ValidationError as e:
            return get_validation_error_response(validation_error=e, http_status_code=400)

        # PAGINATION
        paginator = PageNumberPagination()
        page = paginator.paginate_queryset(restaurants_qs, request)
        if page is not None:
            serializer = RestaurantSerializer(page, many=True)
            return paginator.get_paginated_response(serializer.data)

        serializer = RestaurantSerializer(restaurants_qs, many=True)
        return Response(serializer.data)


class ReservationsView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):

        diners_ids = request.data.get('diners')
        target_datetime_str = request.data.get('target_datetime')
        table_id = request.data.get('table')

        try:
            new_reservation = restaurants.services.restaurants_service.create_reservation(
                diners=diners_ids,
                target_datetime=target_datetime_str,
                table=table_id
            )
        except rest_framework.exceptions.ValidationError as e:
            return get_validation_error_response(validation_error=e, http_status_code=400)
        except custom_errors.DinerWithOverlappingReservationError as e:
            return get_business_requirement_error_response(business_logic_error=e, http_status_code=409)
        except custom_errors.ReservationForAPastTimeError as e:
            return get_business_requirement_error_response(business_logic_error=e, http_status_code=409)
        except custom_errors.TableCanNotHoldDinersQtyError as e:
            return get_business_requirement_error_response(business_logic_error=e, http_status_code=409)
        except custom_errors.TableOccupiedError as e:
            return get_business_requirement_error_response(business_logic_error=e, http_status_code=409)
        except custom_errors.RestaurantDoesntMatchAllDinersDietRestrictionsError as e:
            return get_business_requirement_error_response(business_logic_error=e, http_status_code=409)

        reservation_serializer = ReservationSerializer(new_reservation)
        return Response(reservation_serializer.data, status=200)

    def delete(self, request, pk):
        reservation = get_object_or_404(Reservation, pk=pk)
        reservation.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
