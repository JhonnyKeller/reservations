from django.shortcuts import render

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.views import TokenObtainPairView
from django.contrib.auth.models import User

from django.contrib.auth.hashers import make_password
from rest_framework import status

from ..models import (
    restaurants, placeOfTable, tables, restaurantOpenDaysOfTheWeek,
    closedExceptions, estimatedTimeCustomersSpend, limitOfCustomersPerHour,
    numberOfPeopleWhenTablesConnect, reservations
)
from ..serializers import (
    RestaurantsSerializer, PlaceOfTableSerializer, TablesSerializer,
    RestaurantOpenDaysOfTheWeekSerializer, ClosedExceptionsSerializer,
    EstimatedTimeCustomersSpendSerializer, LimitOfCustomersPerHourSerializer,
    NumberOfPeopleWhenTablesConnectSerializer, ReservationsSerializer, UserSerializer, 
    UserSerializerWithToken)


 


class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    # @classmethod
    # def get_token(cls, user):
    #     token = super().get_token(user)

        # Add custom claims
        # token['username'] = user.username
        # token['message'] = 'message here'
        # ...

    def validate(self, attrs):
        data = super().validate(attrs)
        serializer = UserSerializerWithToken(self.user).data
        for k, v in serializer.items():
            data[k] = v
        return data
    
class TokenObtainPairView(TokenObtainPairView):
    serializer_class = MyTokenObtainPairSerializer

@api_view(['POST'])
def registerUser(request):
    try:
        data = request.data
        print('data:',data)
        user = User.objects.create(
            first_name=data['name'],
            username=data['email'],
            email=data['email'],
            password=make_password(data['password']),
        )
        serializer = UserSerializerWithToken(user, many=False)
        return Response(serializer.data)
    except:
        message = {'detail':'user with this email already exists'}
        return Response(message, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def getUserProfile(request):
    user = request.user
    serializer = UserSerializer(user, many=False)
    return Response(serializer.data)

@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def updateUserProfile(request):
    user = request.user
    serializer = UserSerializerWithToken(user, many=False)
    data = request.data
    user.first_name = data['name']
    user.username = data['email']
    user.email = data['email']
    if data['password'] != '':
        user.password =make_password(data['password'])
    
    user.save()

    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([IsAdminUser])
def getUsers(request):
    users = User.objects.all()
    serializer = UserSerializer(users, many=True)
    return Response(serializer.data)
