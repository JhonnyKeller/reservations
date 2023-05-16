from django.urls import path
from base.views import reservations_views as views

from rest_framework_simplejwt.views import (
    TokenRefreshView,
)

urlpatterns = [
    path('get/shifts/', views.getShifts, name='shifts'),
    path('get/blockeddates/<int:id>/', views.getClosedExceptionsDaysFromRestaurant, name='blockeddates'),
    path('get/blockedweekdays/<int:id>/', views.getClosedWeekDaysFromRestaurant, name='blockedweekdays'),
    path('post/getavailabletimes/', views.getAvailableTimes, name='getAvailableTimes'),
    path('post/createReservation/', views.createReservation, name='createReservation'),
    path('cancel_reservation/<str:token>/', views.cancelReservation, name='cancel_reservation'),
    path('edit_reservation/<uuid:token>/', views.editReservation, name='edit_reservation'),
    path('customersmenu/<str:token>/<str:confirm_or_not>', views.reservationCustomersMenu.as_view(), name='reservation_customersmenu'),
    path('reservation-limits/<int:restaurant_id>', views.restaurant_reservation_limits, name='restaurant_reservation_limits'),
]