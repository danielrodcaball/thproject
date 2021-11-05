from django.urls import path

from restaurants.api.views import RestaurantsView, ReservationsView

app_name = 'restaurants'

urlpatterns = [
    path('restaurants/', RestaurantsView.as_view()),
    path('reservations/', ReservationsView.as_view()),
    path('reservations/<pk>', ReservationsView.as_view(), name='delete_reservation'),
]