from django.contrib import admin
from restaurants.models import DietType, Restaurant, Table, Diner
from restaurants.models.reservation import Reservation


class DietTypeAdmin(admin.ModelAdmin):
    list_display = 'name',


class ReservationAdmin(admin.ModelAdmin):
    list_display = 'datetime',


class RestaurantAdmin(admin.ModelAdmin):
    list_display = ('name', 'location_lat', 'location_long')


class TableAdmin(admin.ModelAdmin):
    list_display = ('capacity', 'restaurant')


class DinerAdmin(admin.ModelAdmin):
    list_display = 'name',


admin.site.register(DietType, DietTypeAdmin)
admin.site.register(Reservation, ReservationAdmin)
admin.site.register(Restaurant, RestaurantAdmin)
admin.site.register(Table, TableAdmin)
admin.site.register(Diner, DinerAdmin)
