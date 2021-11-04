from rest_framework import mixins
from rest_framework.generics import GenericAPIView
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

import restaurants.services.restaurants_service
import rest_framework.exceptions
from rest_framework.pagination import PageNumberPagination

from restaurants.api.serializers import RestaurantSerializer


def get_validation_error_response(validation_error: rest_framework.exceptions.ValidationError, http_status_code: int):
    response = {
        'errors': {
            'display_error': 'Validation Error',
            'field_errors': validation_error.detail
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
