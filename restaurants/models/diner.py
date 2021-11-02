from django.db import models
from restaurants.models.diettype import DietType


class Diner(models.Model):
    name = models.CharField(max_length=255, verbose_name='Name')
    diet_types = models.ManyToManyField(to=DietType, blank=True)
    house_location_lat = models.FloatField(verbose_name="Home Location Latitude")
    house_location_long = models.FloatField(verbose_name="Home Location Longitude")
