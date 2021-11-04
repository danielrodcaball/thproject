from django.urls import path

from restaurants.api.views import FindRestaurantsView

app_name = 'restaurants'

urlpatterns = [
    path('restaurants/', FindRestaurantsView.as_view()),
]