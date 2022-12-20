from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

app_name = 'restaurantsview'

urlpatterns = [
    path('createrestaurant/',views.createrestaurant, name='createrestaurant'),
    path('restaurantmenu/<restaurant_pk>/',views.restaurantmenu, name='restaurantmenu'),
    path('restaurantzones/<restaurant_pk>/',views.createZones, name='restaurantzones'),
    path('restauranttables/<restaurant_pk>/',views.createTables, name='restauranttables'),
    path('restaurantConnectTables/<restaurant_pk>/',views.connectTables, name='restaurantConnectTables'),
    path('restaurantOpenDays/<restaurant_pk>/',views.openDays, name='restaurantOpenDays'),
    path('restaurantClosedDays/<restaurant_pk>/',views.closedDays, name='restaurantClosedDays'),
    path('restaurantEstimatedTime/<restaurant_pk>/',views.estimatedTime, name='restaurantEstimatedTime'),
    path('restaurantLimitOfCustomersPerHour/<restaurant_pk>/',views.limitOfCustomersPerHours, name='restaurantLimitOfCustomersPerHour'),
    path('restaurantsettings/<restaurant_pk>/',views.restaurantSettings, name='restaurantSettings'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
