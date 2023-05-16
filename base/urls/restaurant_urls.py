from django.urls import path
from base.views import restaurant_views as views

from rest_framework_simplejwt.views import (
    TokenRefreshView,
)

urlpatterns = [
    path('', views.getRestaurants, name="restaurants"),
    path('restaurantsFromUser/<str:user>', views.getRestaurantsFromUser, name="restaurantsFrom"),
    path('restaurantfromuser/<int:pk>', views.RestaurantsDetailAPI.as_view(), name="restaurantFrom"),
    path('accept_reservation_from_restaurant/<str:token>', views.postAcceptReservationFromRestaurant, name="accept_reservation_from_restaurant"),
    path('available_tables/<int:restaurant_id>/<str:date>/<str:choosentime>/<str:zone>/<str:tablesused>', views.AvailableTables.as_view(), name='available_tables'),
    path('update_reservation_tables/', views.update_reservation_tables, name='update_reservation'),
    path('time_slots/<int:restaurant_id>/', views.TimeSlotsAPIView.as_view(), name='time_slots'),
    path('<int:restaurant_id>/zones/<int:place_of_table_id>/delete-tables/<int:qty_to_delete>/', views.DeleteTables.as_view(), name='delete_tables'),

    path('<int:user_id>/restaurants/', views.RestaurantsAPI.as_view(), name='restaurants'),
    path('details/<int:pk>', views.RestaurantsDetailAPI.as_view(), name='restaurant_detail'),
    path('<int:restaurant_id>/placeoftable/', views.PlaceOfTableAPI.as_view(), name='place_of_table'),
    path('<int:restaurant_id>/placeoftable/<int:pk>/', views.PlaceOfTableDetailAPI.as_view(), name='place_of_table_detail'),
    path('<int:restaurant_id>/tables/', views.TablesAPI.as_view(), name='tables'),
    path('<int:restaurant_id>/tables/<int:pk>/', views.TablesDetailAPI.as_view(), name='tables_detail'),
    path('<int:restaurant_id>/opentimes/', views.RestaurantOpenDaysOfTheWeekAPI.as_view(), name='open_days'),
    path('<int:restaurant_id>/opentimes/<int:pk>/', views.RestaurantOpenDaysOfTheWeekDetailAPI.as_view(), name='open_days_detail'),
    path('<int:restaurant_id>/closedexceptions/', views.ClosedExceptionsAPI.as_view(), name='closed_exceptions'),
    path('<int:restaurant_id>/closedexceptions/<int:pk>/', views.ClosedExceptionsDetailAPI.as_view(), name='closed_exceptions_detail'),
    path('<int:restaurant_id>/estimatedtime/', views.EstimatedTimeCustomersSpendAPI.as_view(), name='estimated_time'),
    path('<int:restaurant_id>/estimatedtime/<int:pk>/', views.EstimatedTimeCustomersSpendDetailAPI.as_view(), name='estimated_time_detail'),
    path('<int:restaurant_id>/limitcustomerperhour/', views.LimitOfCustomersPerHourAPI.as_view(), name='limit_customers_per_hour'),
    path('<int:restaurant_id>/limitcustomerperhour/<int:pk>/', views.LimitOfCustomersPerHourDetailAPI.as_view(), name='limit_customers_per_hour_detail'),
    path('<int:restaurant_id>/numberofpeopleperconnectedtable/', views.NumberOfPeopleWhenTablesConnectAPI.as_view(), name='number_of_people_connected_tables'),
    path('<int:restaurant_id>/numberofpeopleperconnectedtable/<int:pk>/', views.NumberOfPeopleWhenTablesConnectDetailAPI.as_view(), name='number_of_people_connected_tables_detail'),
    path('<int:restaurant_id>/reservations/', views.ReservationsAPI.as_view(), name='reservations'),
    path('<int:restaurant_id>/reservations/<int:pk>/', views.ReservationsDetailAPI.as_view(), name='reservations_detail'),
]