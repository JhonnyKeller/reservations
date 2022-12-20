from django.urls import path
from . import views

app_name = 'reservations'

urlpatterns = [
    path('<username>/<restaurantname>/',views.reservationss, name='restaurant_reservation'),
    # path('validate/',views.validate, name='validate'),
]
