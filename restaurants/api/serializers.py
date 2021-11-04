from datetime import timezone
from rest_framework import serializers

from restaurants.models import Diner, Restaurant, DietType


class FindRestaurantsValidator(serializers.Serializer):
    diners_ids = serializers.ListField(allow_empty=True)
    target_datetime = serializers.DateTimeField(default_timezone=timezone.utc, allow_null=True)

    def validate_diners_ids(self, value):
        for diner_id in value:
            if not Diner.objects.filter(id=diner_id).exists():
                raise serializers.ValidationError('Diner with id {id} does not exist'.format(id=diner_id))

        return value


class DietTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = DietType
        fields = '__all__'


class RestaurantSerializer(serializers.ModelSerializer):
    diet_endorsement_types = DietTypeSerializer(many=True)

    class Meta:
        model = Restaurant
        fields = '__all__'
