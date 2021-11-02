from django.db import models
from restaurants.models.diettype import DietType


class Restaurant(models.Model):
    name = models.CharField(max_length=255, verbose_name='Name')
    open_time = models.TimeField()
    close_time = models.TimeField()
    diet_type_endorsements = models.ManyToManyField(to=DietType, blank=True)
    location_lat = models.FloatField(verbose_name='Location Latitude')
    location_long = models.FloatField(verbose_name='Location Longitude')

    def __str__(self):
        return self.name

