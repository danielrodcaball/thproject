from django.db import models
from restaurants.models.restaurant import Restaurant


class Table(models.Model):
    capacity = models.IntegerField(verbose_name='Capacity')
    restaurant = models.ForeignKey(to=Restaurant, on_delete=models.CASCADE)
