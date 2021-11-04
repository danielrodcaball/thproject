from datetime import timezone, datetime
from rest_framework import serializers
from rest_framework.relations import PrimaryKeyRelatedField

from restaurants.models import Diner, Restaurant, DietType, Table
from restaurants.models.reservation import Reservation


class FindRestaurantsValidator(serializers.Serializer):
    diners = PrimaryKeyRelatedField(allow_empty=True, many=True, queryset=Diner.objects.all())
    target_datetime = serializers.DateTimeField(default_timezone=timezone.utc, allow_null=True)


class DietTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = DietType
        fields = '__all__'


class RestaurantSerializer(serializers.ModelSerializer):
    diet_endorsement_types = DietTypeSerializer(many=True)

    class Meta:
        model = Restaurant
        fields = '__all__'


class ReservationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Reservation
        fields = ['id', 'diners', 'table', 'datetime']