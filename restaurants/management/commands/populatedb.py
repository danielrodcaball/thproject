from datetime import datetime, timezone

from django.core.management.base import BaseCommand

from restaurants.models import DietType, Diner, Restaurant, Table
from restaurants.models.reservation import Reservation


class Command(BaseCommand):

    def handle(self, *args, **options):
        pass
