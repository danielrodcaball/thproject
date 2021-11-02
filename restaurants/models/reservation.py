from django.db import models
from restaurants.models.diner import Diner
from restaurants.models.table import Table


class Reservation(models.Model):
    diners = models.ManyToManyField(to=Diner)
    table = models.ForeignKey(to=Table, on_delete=models.CASCADE)
    datetime = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Created at')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Updated at')
