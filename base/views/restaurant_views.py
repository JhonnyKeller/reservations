from django.shortcuts import render
from rest_framework import generics
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.views import TokenObtainPairView
from django.contrib.auth.models import User
from django.template import loader
from django.core.mail import EmailMultiAlternatives
from django.contrib import messages
from django.db.models import Case, When, IntegerField
from rest_framework.views import APIView
from django.http import JsonResponse
from datetime import datetime
from django.contrib.auth.hashers import make_password
from rest_framework import status
from django.shortcuts import get_object_or_404
from django.core.exceptions import ValidationError
from django.db.models.functions import Cast
from django.db.models import IntegerField

from ..models import (
    restaurants, placeOfTable, tables, restaurantOpenDaysOfTheWeek,
    closedExceptions, estimatedTimeCustomersSpend, limitOfCustomersPerHour,
    numberOfPeopleWhenTablesConnect, reservations
)
from ..serializers import (
    RestaurantsSerializer, PlaceOfTableSerializer, TablesSerializer,
    RestaurantOpenDaysOfTheWeekSerializer, ClosedExceptionsSerializer,
    EstimatedTimeCustomersSpendSerializer, LimitOfCustomersPerHourSerializer,
    NumberOfPeopleWhenTablesConnectSerializer, ReservationsSerializer
)
from base.views.reservations_views import send_sms



class RestaurantsAPI(generics.ListCreateAPIView):
    queryset = restaurants.objects.all()
    serializer_class = RestaurantsSerializer

    def get_queryset(self):
        user_id = self.kwargs['user_id']
        return restaurants.objects.filter(owner__pk=user_id)

class RestaurantsDetailAPI(generics.RetrieveUpdateDestroyAPIView):
    queryset = restaurants.objects.all()
    serializer_class = RestaurantsSerializer

    def put(self, request, *args, **kwargs):
        try:
            print("Request data:", request.data)  # Add this print statement
            return super().update(request, *args, **kwargs)
        except ValidationError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

class PlaceOfTableAPI(generics.ListCreateAPIView):
    queryset = placeOfTable.objects.all()
    serializer_class = PlaceOfTableSerializer

    def get_queryset(self):
        restaurant_id = self.kwargs['restaurant_id']
        return placeOfTable.objects.filter(restaurant__id=restaurant_id)

class PlaceOfTableDetailAPI(generics.RetrieveUpdateDestroyAPIView):
    queryset = placeOfTable.objects.all()
    serializer_class = PlaceOfTableSerializer

class TablesAPI(generics.ListCreateAPIView):
    queryset = tables.objects.all()
    serializer_class = TablesSerializer

    def get_queryset(self):
        restaurant_id = self.kwargs['restaurant_id']
        return (
            tables.objects.filter(restaurant__id=restaurant_id)
            .annotate(table_number_int=Cast("table_number", IntegerField()))
            .order_by("place_of_table", "table_number_int")
        )

    def create_tables(self, restaurant, place_of_table, num_tables_to_create, num_seats):
        # Find the highest table_number
        max_table_number = (
            tables.objects.filter(restaurant=restaurant, place_of_table=place_of_table)
            .annotate(table_number_int=Cast("table_number", IntegerField()))
            .order_by("-table_number_int")
            .first()
        )

        start_number = (
            int(max_table_number.table_number) + 1 if max_table_number else 1
        )
        end_number = start_number + num_tables_to_create

        # Create the new tables
        new_tables = [
            tables(
                restaurant=restaurant,
                table_number=str(i),
                number_of_seats=num_seats,
                place_of_table=place_of_table,
                can_connect_tables=""
            )
            for i in range(start_number, end_number)
        ]

        # Save the new tables
        tables.objects.bulk_create(new_tables)

    def post(self, request, *args, **kwargs):
        restaurant_id = self.kwargs['restaurant_id']
        place_of_table_id = request.data.get("place_of_table")
        num_tables_to_create = int(request.data.get("num_tables_to_create"))
        num_seats = request.data.get("num_seats")

        if not all([place_of_table_id, num_tables_to_create, num_seats]):
            return Response(
                {"error": "Invalid data"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        restaurant = restaurants.objects.get(id=restaurant_id)
        place_of_table = placeOfTable.objects.get(id=place_of_table_id)

        self.create_tables(restaurant, place_of_table, num_tables_to_create, num_seats)

        return Response(
            {"message": "Tables created successfully"},
            status=status.HTTP_201_CREATED,
        )

class TablesDetailAPI(generics.RetrieveUpdateDestroyAPIView):
    queryset = tables.objects.all()
    serializer_class = TablesSerializer

class RestaurantOpenDaysOfTheWeekAPI(generics.ListCreateAPIView):
    queryset = restaurantOpenDaysOfTheWeek.objects.all()
    serializer_class = RestaurantOpenDaysOfTheWeekSerializer

    def get_queryset(self):
        restaurant_id = self.kwargs['restaurant_id']
        return restaurantOpenDaysOfTheWeek.objects.filter(restaurant__id=restaurant_id)

    def create(self, request, *args, **kwargs):
        print("Request data:", request.data)
        serializer = self.get_serializer(data=request.data)
        if not serializer.is_valid():
            print("Serializer errors:", serializer.errors)
            return JsonResponse(serializer.errors, status=400)

        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return JsonResponse(serializer.data, status=201, headers=headers)

class RestaurantOpenDaysOfTheWeekDetailAPI(generics.RetrieveUpdateDestroyAPIView):
    queryset = restaurantOpenDaysOfTheWeek.objects.all()
    serializer_class = RestaurantOpenDaysOfTheWeekSerializer

class ClosedExceptionsAPI(generics.ListCreateAPIView):
    queryset = closedExceptions.objects.all()
    serializer_class = ClosedExceptionsSerializer

    def get_queryset(self):
        restaurant_id = self.kwargs['restaurant_id']
        return closedExceptions.objects.filter(restaurant__id=restaurant_id)

class ClosedExceptionsDetailAPI(generics.RetrieveUpdateDestroyAPIView):
    queryset = closedExceptions.objects.all()
    serializer_class = ClosedExceptionsSerializer

class EstimatedTimeCustomersSpendAPI(generics.ListCreateAPIView):
    queryset = estimatedTimeCustomersSpend.objects.all()
    serializer_class = EstimatedTimeCustomersSpendSerializer

    def get_queryset(self):
        restaurant_id = self.kwargs['restaurant_id']
        return estimatedTimeCustomersSpend.objects.filter(restaurant__id=restaurant_id)

class EstimatedTimeCustomersSpendDetailAPI(generics.RetrieveUpdateDestroyAPIView):
    queryset = estimatedTimeCustomersSpend.objects.all()
    serializer_class = EstimatedTimeCustomersSpendSerializer

class LimitOfCustomersPerHourAPI(generics.ListCreateAPIView):
    queryset = limitOfCustomersPerHour.objects.all()
    serializer_class = LimitOfCustomersPerHourSerializer

    def get_queryset(self):
        restaurant_id = self.kwargs['restaurant_id']
        return limitOfCustomersPerHour.objects.filter(restaurant__id=restaurant_id)

class LimitOfCustomersPerHourDetailAPI(generics.RetrieveUpdateDestroyAPIView):
    queryset = limitOfCustomersPerHour.objects.all()
    serializer_class = LimitOfCustomersPerHourSerializer

class NumberOfPeopleWhenTablesConnectAPI(generics.ListCreateAPIView):
    queryset = numberOfPeopleWhenTablesConnect.objects.all()
    serializer_class = NumberOfPeopleWhenTablesConnectSerializer

    def get_queryset(self):
        restaurant_id = self.kwargs['restaurant_id']
        return numberOfPeopleWhenTablesConnect.objects.filter(restaurant__id=restaurant_id)

class NumberOfPeopleWhenTablesConnectDetailAPI(generics.RetrieveUpdateDestroyAPIView):
    queryset = numberOfPeopleWhenTablesConnect.objects.all()
    serializer_class = NumberOfPeopleWhenTablesConnectSerializer

class ReservationsAPI(generics.ListCreateAPIView):
    serializer_class = ReservationsSerializer

    def get_queryset(self):
        restaurant_id = self.kwargs['restaurant_id']
        date = self.request.query_params.get('dateFilter', None)
        shift = self.request.query_params.get('shift', None)
        place_of_table = self.request.query_params.get('place_of_table', None)
        status = self.request.query_params.get('status', None)

        queryset = reservations.objects.filter(restaurant__id=restaurant_id)

        if date is not None:
            queryset = queryset.filter(date__contains=date)

        if shift is not None:
            queryset = queryset.filter(shift__contains=shift)
        
        if place_of_table is not None:
            queryset = queryset.filter(table_place_preference__place_of_table__contains=place_of_table)

        if status is not None:
            queryset = queryset.filter(status__contains=status)

        # Define custom ordering
        custom_ordering = Case(
            When(status='Accepted', then=0),
            When(status='Pending_from_restaurant', then=1),
            When(status='Edited', then=2),
            When(status='Pending_from_customer', then=3),
            When(status='Cancelled', then=4),
            output_field=IntegerField()
        )

        return queryset.annotate(ordering=custom_ordering).order_by('ordering', 'time')
    
class DeleteTables(APIView):
    def delete(self, request, restaurant_id, place_of_table_id, qty_to_delete):
        table_ids_to_delete = (
            tables.objects
            .filter(restaurant_id=restaurant_id, place_of_table_id=place_of_table_id)
            .annotate(table_number_int=Cast("table_number", IntegerField()))
            .order_by("-table_number_int")
            .values_list("id", flat=True)
            [:int(qty_to_delete)]
        )
        
        deleted_count = len(table_ids_to_delete)
        tables.objects.filter(id__in=table_ids_to_delete).delete()

        return Response({"message": f"Deleted {deleted_count} tables."}, status=status.HTTP_204_NO_CONTENT)

class ReservationsDetailAPI(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = ReservationsSerializer

    def get_queryset(self):
        restaurant_id = self.kwargs['restaurant_id']
        date = self.request.query_params.get('dateFilter', None)
        shift = self.request.query_params.get('shift', None)
        place_of_table = self.request.query_params.get('place_of_table', None)

        queryset = reservations.objects.filter(restaurant__id=restaurant_id)

        if date is not None:
            queryset = queryset.filter(date__contains=date)

        if shift is not None:
            queryset = queryset.filter(shift__contains=shift)
        
        if place_of_table is not None:
            queryset = queryset.filter(table_place_preference__place_of_table__contains=place_of_table)

        return queryset.order_by('time')

    def get_object(self):
        queryset = self.get_queryset()
        obj = get_object_or_404(queryset, pk=self.kwargs['pk'])
        return obj

@api_view(['GET'])
def getRestaurants(request):
    restaurants_data = restaurants.objects.all()
    serializer = RestaurantsSerializer(restaurants_data, many=True)
    return Response(serializer.data)

@api_view(['GET'])
def getRestaurantsFromUser(request, user):
    restaurant = []
    for i in restaurants:
        if i['email'] == user:
            restaurant.append(i)
    return Response(restaurant)

@api_view(['GET'])
def getRestaurantFromUser(request, id):
    restaurant_data = restaurants.objects.filter(pk__exact=id)
    print(restaurant_data)
    serializer = RestaurantsSerializer(restaurant_data, many=True)
    return Response(serializer.data)

@api_view(['GET'])
def getReservationsFromRestaurant(request, id):
    restaurant_data = restaurants.objects.filter(pk__exact=id)
    print(restaurant_data)
    serializer = RestaurantsSerializer(restaurant_data, many=True)
    return Response(serializer.data)

@api_view(['POST'])
def postAcceptReservationFromRestaurant(request, token):
    try:
        reservation = reservations.objects.get(token=token)
        reservation.status = 'Accepted'
        reservation.save()
        message = {'detail': 'Reserva editada'}
        serializer = ReservationsSerializer(reservation, many=False)
        send_sms(reservation.phone_number, 'A sua reserva foi aceite e pode acessa-la em http://localhost:3000/{}'.format(token))
        link_to_reservation_menu = 'http://localhost:3000/customer_reservation_menu/' + str(reservation.token) + '/accepted'
        template = loader.get_template('accepted_reservation.txt')
        email_context = {
            'name':reservation.full_name,
            'email':reservation.email,
            'day':reservation.date,
            'time':reservation.time,
            'shift':reservation.shift,
            'restaurant':reservation.restaurant.restaurant_name,
            'phone_number':reservation.phone_number,
            'link_to_reservation_menu':link_to_reservation_menu,
        }
        message = template.render(email_context)
        email_forclient = EmailMultiAlternatives (
            reservation.restaurant.restaurant_name, message,
            'jhonnykellerdev@gmail.com',
            [reservation.email],
        )
        # Convert the html and css inside the [contact_form.txt] to HTML templete
        email_forclient.content_subtype = 'html'
        email_forclient.send()
        return Response(serializer.data)
    except Exception as e:
        message = {'detail': f'There was a problem with the reservation: {str(e)}'}
        return Response(message, status=status.HTTP_400_BAD_REQUEST)

class AvailableTables(APIView):
    def get(self, request, restaurant_id, date, choosentime, zone, tablesused, format=None):
        result = []

        # Convert choosentime to a datetime object
        choosentime = datetime.strptime(choosentime, '%H:%M')

        # Get all place_of_table for the given restaurant
        places = placeOfTable.objects.filter(restaurant_id=restaurant_id)

        # Loop through each place_of_table and get available tables
        for place in places:
            place_result = [place.place_of_table]
            all_tables = tables.objects.filter(restaurant_id=restaurant_id, place_of_table=place)

            # Get all reservations for the given restaurant, date, and place_of_table
            reserved_tables = reservations.objects.filter(restaurant_id=restaurant_id, date=date, table_place_preference=place)

            # Create a list with all reserved table numbers
            reserved_table_numbers = []
            for r in reserved_tables:
                # Check if choosentime is within the reservation time range
                reservation_time = datetime.strptime(r.time, '%H:%M')
                reservation_estimatedtime = datetime.strptime(r.estimatedtime, '%H:%M')

                if choosentime >= reservation_time and choosentime <= reservation_estimatedtime:
                    reserved_table_numbers.extend(r.tablesused.split(','))

            # Exclude tablesused from the list of reserved tables
            print('hereeeeeeeeeeeeeee')
            print(zone)
            print(place.pk)
            if str(zone) == str(place.pk):
                if tablesused and tablesused != 'no_tables':
                    tablesused_list = tablesused.split(',')
                    reserved_table_numbers = list(set(reserved_table_numbers) - set(tablesused_list))

            # Get available tables by excluding reserved tables
            available_tables = all_tables.exclude(table_number__in=reserved_table_numbers)

            for table in available_tables:
                place_result.append(table.table_number)
            result.append(place_result)
        print('result')
        print(result)

        return JsonResponse(result, safe=False)
    
@api_view(['POST'])
def update_reservation_tables(request):
    try:
        token = request.data['token']
        dic = request.data.get('dictionarie')
        id = request.data['id']
        reservation = reservations.objects.get(token=token)
    except reservations.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    if dic:  # Check if the dictionary is not empty
        table_place_preference_name, tablesused_list = next(iter(dic.items()))

        try:
            table_place_preference = placeOfTable.objects.get(restaurant__pk__exact=id,place_of_table=table_place_preference_name)
        except placeOfTable.DoesNotExist:
            return Response(status=status.HTTP_400_BAD_REQUEST)

        if tablesused_list:  # Check if the list is not empty
            tablesused = ','.join(tablesused_list)
            if tablesused[:1] == ',':
                tablesused = tablesused[1:]
        else:
            tablesused = ''

        print('table_place_preference')
        print(table_place_preference)

        reservation.table_place_preference = table_place_preference
        reservation.tablesused = tablesused
        reservation.save()

        serializer = ReservationsSerializer(reservation)
        return Response(serializer.data)
    else:
        return Response(status=status.HTTP_400_BAD_REQUEST)
    
class TimeSlotsAPIView(APIView):
    def get(self, request, restaurant_id):
        restaurant = get_object_or_404(restaurants, id=restaurant_id)
        each_time = restaurant.each_time
        hours, minutes = map(int, each_time.split(':'))
        total_minutes = hours * 60 + minutes

        slots = []
        current_time = 0

        while current_time < 24 * 60:
            hours, minutes = divmod(current_time, 60)
            slots.append(f'{hours:02d}:{minutes:02d}')
            current_time += total_minutes

        return Response(slots)