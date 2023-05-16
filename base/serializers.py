from rest_framework import serializers
from django.contrib.auth.models import User
from rest_framework_simplejwt.tokens import RefreshToken
from .models import (restaurants,placeOfTable,tables,restaurantOpenDaysOfTheWeek,
                    closedExceptions,estimatedTimeCustomersSpend,
                    numberOfPeopleWhenTablesConnect,limitOfCustomersPerHour,reservations)


class UserSerializer(serializers.ModelSerializer):
    name = serializers.SerializerMethodField(read_only=True)
    isAdmin =serializers.SerializerMethodField(read_only=True)
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'name', 'isAdmin']

    def get_isAdmin(self, obj):
        isAdmin = obj.is_staff
        return isAdmin
    
    def get_name(self, obj):
        name = obj.first_name
        if name == '':
            name = obj.email
        return name

class UserSerializerWithToken(UserSerializer):
    token = serializers.SerializerMethodField(read_only=True)
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'name', 'isAdmin', 'token']

    def get_token(self, obj):
        token = RefreshToken.for_user(obj)
        return str(token.access_token)


class RestaurantsSerializer(serializers.ModelSerializer):
    class Meta:
        model = restaurants
        fields = '__all__'

class PlaceOfTableSerializer(serializers.ModelSerializer):
    class Meta:
        model = placeOfTable
        fields = '__all__'

class TablesSerializer(serializers.ModelSerializer):
    class Meta:
        model = tables
        fields = '__all__'

class RestaurantOpenDaysOfTheWeekSerializer(serializers.ModelSerializer):
    class Meta:
        model = restaurantOpenDaysOfTheWeek
        fields = '__all__'

class ClosedExceptionsSerializer(serializers.ModelSerializer):
    class Meta:
        model = closedExceptions
        fields = '__all__'

class EstimatedTimeCustomersSpendSerializer(serializers.ModelSerializer):
    class Meta:
        model = estimatedTimeCustomersSpend
        fields = '__all__'

class LimitOfCustomersPerHourSerializer(serializers.ModelSerializer):
    class Meta:
        model = limitOfCustomersPerHour
        fields = '__all__'

class NumberOfPeopleWhenTablesConnectSerializer(serializers.ModelSerializer):
    class Meta:
        model = numberOfPeopleWhenTablesConnect
        fields = '__all__'

class ReservationsSerializer(serializers.ModelSerializer):
    table_place_preference = PlaceOfTableSerializer()
    class Meta:
        model = reservations
        fields = '__all__'