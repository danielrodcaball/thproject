from django.urls import path

from restaurants.api.views import RestaurantsView

app_name = 'restaurants'

urlpatterns = [
    path('restaurants/', RestaurantsView.as_view()),
]