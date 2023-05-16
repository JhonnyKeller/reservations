from django.shortcuts import render
from django.shortcuts import get_object_or_404
from django.http import JsonResponse
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.views import TokenObtainPairView
from django.contrib.auth.models import User
from datetime import datetime, timedelta
from base.views.assign_tables_function import assignThTables
from rest_framework import generics
import uuid
from twilio.rest import Client
from django.conf import settings

from django.template import loader
from django.core.mail import EmailMultiAlternatives
from django.contrib import messages

from django.contrib.auth.hashers import make_password
from rest_framework import status

from base.models import (
    restaurants, placeOfTable, tables, restaurantOpenDaysOfTheWeek,
    closedExceptions, estimatedTimeCustomersSpend, limitOfCustomersPerHour,
    numberOfPeopleWhenTablesConnect, reservations
)
from base.serializers import (
    RestaurantsSerializer, PlaceOfTableSerializer, TablesSerializer,
    RestaurantOpenDaysOfTheWeekSerializer, ClosedExceptionsSerializer,
    EstimatedTimeCustomersSpendSerializer, LimitOfCustomersPerHourSerializer,
    NumberOfPeopleWhenTablesConnectSerializer, ReservationsSerializer
)
import re

def send_sms(to, body):
    print('here4')
    client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
    print('here5')
    print(to)
    print(body)
    print(settings.TWILIO_PHONE_NUMBER)
    try:
        message = client.messages.create(
            body=body,
            from_=settings.TWILIO_PHONE_NUMBER,
            to=to
        )
        print('here6')
        return message.sid
    except Exception as e:
        print(f"Error sending SMS: {e}")
        return None

def verify_hour_availability(time_to_check,start_time,end_time,estimated_time):
    time_to_check = datetime.strptime(time_to_check, '%H:%M:%S')
    start_time += ':00'
    start_time = datetime.strptime(start_time, '%H:%M:%S')
    end_time += ':00'
    end_time = datetime.strptime(end_time, '%H:%M:%S')
    estimated_time = estimated_time.split(":")
    if time_to_check >= start_time and time_to_check <= end_time:
        return False
    time_to_check = time_to_check + timedelta(hours=int(estimated_time[0]),minutes=int(estimated_time[1]))
    if time_to_check >= start_time and time_to_check <= end_time:
        return False

    return True



def find_tables(the_hours,estimated_time,can_connect_list,used_table_list,save_necessary_people,connect_logic_number,tables_used,connect_logic, placeOfTables):
    print('(----------------- find tables start ----------------)')
    print('zone:', placeOfTables)
    print('can_connect_list:',can_connect_list)
    print('tables_used:',tables_used)
    print('save_necessary_people:',save_necessary_people)
    print('connect_logic_number:',connect_logic_number)
    print('connect_logic:',connect_logic)
    print('used_table_list:',used_table_list)
    print('the_hours:',the_hours)
    print('estimated_time:',estimated_time)
    if can_connect_list == ['']:
        return 0
    found_table = 3
    for utl in range(0, len(used_table_list), 1):
        for ccll in can_connect_list:
            if ccll == used_table_list[utl]:
                can_connect_list.remove(used_table_list[utl])
    for ccl in range(0,len(can_connect_list),1):
        temporary_table = []
        for i in range(0, len(tables_used), 3):
            if can_connect_list != ['']:
                if int(tables_used[i])  == int(can_connect_list[ccl]):
                    temporary_table.append(tables_used[i])
                    temporary_table.append(tables_used[i+1])
                    temporary_table.append(tables_used[i+2])
        verify_hour = False
        if temporary_table != []:
            print('if temporary_table != []: It means there is reservations for the table being verified and it needs to be verified.')
            for tt in range(0,len(temporary_table),3):
                for kk in range(0,len(temporary_table),3):
                    verify_hour = verify_hour_availability(the_hours,temporary_table[kk+1],temporary_table[kk+2],estimated_time)
                    if verify_hour == False:
                        break
                if verify_hour:
                    check_table = tables.objects.filter(table_number__contains=can_connect_list[ccl], place_of_table__place_of_table__contains=placeOfTables)
                    save_necessary_people_two = save_necessary_people
                    save_necessary_people_two -= int(check_table[0].number_of_seats) + connect_logic[connect_logic_number].number_of_chairs
                    used_table_list_one = used_table_list[:]
                    used_table_list_one.append(can_connect_list[ccl])
                    if save_necessary_people_two <= 0:
                        return 1
                    else:
                        if connect_logic_number == 0:
                            connect_logic_number_save = connect_logic_number + 1
                        elif connect_logic_number == 2:
                            connect_logic_number_save = connect_logic_number - 1
                        else:
                            connect_logic_number_save = connect_logic_number + 1
                        can_connect_list_two = check_table[0].can_connect_tables[:]
                        can_connect_list_two = can_connect_list_two.split(',')
                        found_table = find_tables(the_hours,estimated_time,can_connect_list_two,used_table_list_one,save_necessary_people_two,connect_logic_number_save,tables_used,connect_logic, placeOfTables)
                        if found_table == 1:
                            return 1
        if temporary_table == []:
            print('if temporary_table == []: It means there is no reservations for the table being verified and it does not need to be verified.')
            check_table = tables.objects.filter(table_number__contains=can_connect_list[ccl], place_of_table__place_of_table__contains=placeOfTables)
            save_necessary_people_two = save_necessary_people
            save_necessary_people_two -= int(check_table[0].number_of_seats) + connect_logic[connect_logic_number].number_of_chairs
            used_table_list_one = used_table_list[:]
            used_table_list_one.append(can_connect_list[ccl])
            if save_necessary_people_two <= 0:
                return 1
            else:
                if connect_logic_number == 0:
                    connect_logic_number_save = connect_logic_number + 1
                elif connect_logic_number == 2:
                    connect_logic_number_save = connect_logic_number - 1
                else:
                    connect_logic_number_save = connect_logic_number + 1
                can_connect_list_two = check_table[0].can_connect_tables[:]
                can_connect_list_two = can_connect_list_two.split(',')
                found_table = find_tables(the_hours,estimated_time,can_connect_list_two,used_table_list_one,save_necessary_people_two,connect_logic_number_save,tables_used,connect_logic, placeOfTables)
                if found_table == 1:
                    return 1
    return 0


def retrieveAvailableHoursToReservation(tables_used, necessary_people, estimated_time, restaurant_id, hours_list, placeOfTables):
    print('zone:', placeOfTables)
    print('restaurant_id:',restaurant_id)
    print('tables_used:',tables_used)
    print('necessary_people:',necessary_people)
    print('hours_list:',hours_list)
    print('estimated_time:',estimated_time)
    connect_logic = numberOfPeopleWhenTablesConnect.objects.filter(restaurant__pk__exact=restaurant_id)
    restaurant_tables = tables.objects.filter(restaurant__pk__exact=restaurant_id)
    zones = placeOfTable.objects.filter(restaurant__pk__exact=restaurant_id, place_of_table__contains=placeOfTables)
    availabletimes = []
    for x in zones:
        tables_zone = tables.objects.filter(restaurant__pk__exact=restaurant_id,place_of_table__pk__contains=x.pk)
        availabletimes.append(x.place_of_table)
        the_hours = hours_list[:]
        print('------------------zone---------------------')
        print(x)
        for y in tables_zone:
            print('------------------Current table---------------------')
            print(y)
            print('the_hours')
            print(the_hours)
            ii = -1
            for hours_saved in range(0,len(the_hours),1):
                ii += 1
                if ii >= len(the_hours):
                    break
                save_necessary_people = necessary_people
                temporary_table = []
                used_table_list = []
                for i in range(0, len(tables_used), 3):
                    if int(tables_used[i])  == int(y.table_number):
                        temporary_table.append(tables_used[i])
                        temporary_table.append(tables_used[i+1])
                        temporary_table.append(tables_used[i+2])
                verify_hour = False
                if temporary_table != []:
                    print('if temporary_table != []: It means there is reservations for the table being verified and it needs to be verified.')
                    for tt in range(0,len(temporary_table),3):
                        for kk in range(0,len(temporary_table),3):
                            verify_hour = verify_hour_availability(the_hours[ii],temporary_table[kk+1],temporary_table[kk+2],estimated_time)
                            if verify_hour == False:
                                break
                        if verify_hour:
                            save_necessary_people_one = save_necessary_people
                            save_necessary_people_one -= int(y.number_of_seats)
                            used_table_list.append(y.table_number)
                            if save_necessary_people_one <= 0 and temporary_table == []:
                                ni = 0
                                while the_hours != []:
                                    availabletimes.append(the_hours[ni])
                                    the_hours.remove(the_hours[ni])
                                break
                            if save_necessary_people_one <= 0:
                                availabletimes.append(the_hours[ii])
                                the_hours.remove(the_hours[ii])
                                ii -= 1
                            can_connect_list = y.can_connect_tables[:]
                            can_connect_list = can_connect_list.split(',')
                            find_the_table = find_tables(the_hours[ii],estimated_time,can_connect_list,used_table_list,save_necessary_people_one,0,tables_used,connect_logic, placeOfTables)
                            if find_the_table == 1:
                                availabletimes.append(the_hours[ii])
                                the_hours.remove(the_hours[ii])
                                ii -= 1
                if temporary_table == []:
                    print('if temporary_table == []: It means there is no reservations for the table being verified and it does not need to be verified.')
                    save_necessary_people_one = save_necessary_people
                    save_necessary_people_one -= int(y.number_of_seats)
                    used_table_list.append(y.table_number)
                    if save_necessary_people_one <= 0 and temporary_table == []:
                        ni = 0
                        while the_hours != []:
                            availabletimes.append(the_hours[ni])
                            the_hours.remove(the_hours[ni])
                        break
                    if save_necessary_people_one <= 0:
                        availabletimes.append(the_hours[ii])
                        the_hours.remove(the_hours[ii])
                        ii -= 1
                    can_connect_list = y.can_connect_tables[:]
                    can_connect_list = can_connect_list.split(',')
                    find_the_table = find_tables(the_hours[ii],estimated_time,can_connect_list,used_table_list,save_necessary_people_one,0,tables_used,connect_logic, placeOfTables)
                    if find_the_table == 1:
                        availabletimes.append(the_hours[ii])
                        the_hours.remove(the_hours[ii])
                        ii -= 1
    return availabletimes



def retrieveTablesUsed(date, shift, restaurant_id, zone):
    reservation = reservations.objects.filter(restaurant__pk__exact=restaurant_id,
                                             date__exact=date,shift__contains=shift,
                                             table_place_preference__place_of_table__contains=zone)
    
    reservation = reservation.exclude(status__contains='Cancelled').exclude(tablesused__exact='')

    tu = []
    for y in reservation:
        tables_list = y.tablesused.split(",")
        n = 0
        for x in tables_list:
            tu.append(tables_list[n])
            n += 1
            tu.append(y.time)
            tu.append(y.estimatedtime)
    return tu

def return_correct_weekday_filter(restaurant_id,weekday):
    filter = []
    if weekday == 'Monday':
        filter = restaurantOpenDaysOfTheWeek.objects.filter(restaurant__pk__exact=restaurant_id,Monday=True)
    if weekday == 'Tuesday':
        filter = restaurantOpenDaysOfTheWeek.objects.filter(restaurant__pk__exact=restaurant_id,Tuesday=True)
    if weekday == 'Wednesday':
        filter = restaurantOpenDaysOfTheWeek.objects.filter(restaurant__pk__exact=restaurant_id,Wednesday=True)
    if weekday == 'Thursday':
        filter = restaurantOpenDaysOfTheWeek.objects.filter(restaurant__pk__exact=restaurant_id,Thursday=True)
    if weekday == 'Friday':
        filter = restaurantOpenDaysOfTheWeek.objects.filter(restaurant__pk__exact=restaurant_id,Friday=True)
    if weekday == 'Saturday':
        filter = restaurantOpenDaysOfTheWeek.objects.filter(restaurant__pk__exact=restaurant_id,Saturday=True)
    if weekday == 'Sunday':
        filter = restaurantOpenDaysOfTheWeek.objects.filter(restaurant__pk__exact=restaurant_id,Sunday=True)
    return filter

def return_correct_weekday_filter_w_shift(restaurant_id,weekday,shift):
    filter = []
    if weekday == 'Monday':
        filter = restaurantOpenDaysOfTheWeek.objects.filter(restaurant__pk__exact=restaurant_id,Monday=True,shift__contains=shift)
    if weekday == 'Tuesday':
        filter = restaurantOpenDaysOfTheWeek.objects.filter(restaurant__pk__exact=restaurant_id,Tuesday=True,shift__contains=shift)
    if weekday == 'Wednesday':
        filter = restaurantOpenDaysOfTheWeek.objects.filter(restaurant__pk__exact=restaurant_id,Wednesday=True,shift__contains=shift)
    if weekday == 'Thursday':
        filter = restaurantOpenDaysOfTheWeek.objects.filter(restaurant__pk__exact=restaurant_id,Thursday=True,shift__contains=shift)
    if weekday == 'Friday':
        filter = restaurantOpenDaysOfTheWeek.objects.filter(restaurant__pk__exact=restaurant_id,Friday=True,shift__contains=shift)
    if weekday == 'Saturday':
        filter = restaurantOpenDaysOfTheWeek.objects.filter(restaurant__pk__exact=restaurant_id,Saturday=True,shift__contains=shift)
    if weekday == 'Sunday':
        filter = restaurantOpenDaysOfTheWeek.objects.filter(restaurant__pk__exact=restaurant_id,Sunday=True,shift__contains=shift)
    return filter

def checkIfThereIsWeekDay(weekday, value, restaurant):
    weekday = return_correct_weekday_filter(restaurant,weekday)
    if weekday.count() <= 0:
        return value
    return None

def is_valid_time(time_str):
    time_pattern = re.compile(r'^\d{2}:\d{2}:\d{2}$')
    return time_pattern.match(time_str) is not None

def return_weekdays_not_open(restaurant):
    weekdaysnotopen = []
    weekdaysnotopen.append(checkIfThereIsWeekDay('Monday', 1, restaurant))
    weekdaysnotopen.append(checkIfThereIsWeekDay('Tuesday', 2, restaurant))
    weekdaysnotopen.append(checkIfThereIsWeekDay('Wednesday', 3, restaurant))
    weekdaysnotopen.append(checkIfThereIsWeekDay('Thursday', 4, restaurant))
    weekdaysnotopen.append(checkIfThereIsWeekDay('Friday', 5, restaurant))
    weekdaysnotopen.append(checkIfThereIsWeekDay('Saturday', 6, restaurant))
    weekdaysnotopen.append(checkIfThereIsWeekDay('Sunday', 0, restaurant))
    new_string = ''
    for e in weekdaysnotopen:
        if e != None:
            new_string += str(e) + ','
        else:
            new_string += '10,'
    return new_string[:len(new_string)-1]


def numbers_to_weekday(argument):
    switcher = {
        1: "Monday",
        2: "Tuesday",
        3: "Wednesday",
        4: "Thursday",
        5: "Friday",
        6: "Saturday",
        7: "Sunday",
    }
    return switcher.get(argument, '')

def return_estimated_time(number_of_people, restaurant_id):
    estimated_time = estimatedTimeCustomersSpend.objects.filter(restaurant__pk__exact=restaurant_id,number_of_people__gte=number_of_people)
    if estimated_time.count() <= 0:
        estimated_time = estimatedTimeCustomersSpend.objects.filter(restaurant__pk__exact=restaurant_id,number_of_people__lte=number_of_people)
        estimative = estimated_time[estimated_time.count()-1].estimated_time
    else:
        estimative = estimated_time[0].estimated_time
    estimative = estimative.strftime("%H:%M")
    return estimative

def returnStringOfClosedExceptions(restaurant_id):
    closed_days = closedExceptions.objects.filter(restaurant__pk__exact=restaurant_id)
    string = ''
    # choosenday = datetime.strptime(choosenday, '%m/%d/%Y')
    # choosenday = choosenday.strftime("%Y-%m-%d")
    for x in closed_days:
        if int(x.number_of_acceptance) <= 0:
            start_day = x.closed_days_start
            end_day = x.closed_days_end
            lowest_start_time = ''
            higher_end_time = ''
            while start_day <= end_day:
                filter_weekday = return_correct_weekday_filter(restaurant_id,numbers_to_weekday(start_day.isoweekday()))
                for y in filter_weekday:
                    if lowest_start_time == '':
                        lowest_start_time = y.start_time
                    elif lowest_start_time > y.start_time:
                        lowest_start_time = y.start_time
                    if higher_end_time == '':
                        higher_end_time = y.end_time
                    elif higher_end_time < y.end_time:
                        higher_end_time = y.end_time
                if lowest_start_time != '':
                    if lowest_start_time >= x.time_start and higher_end_time <= x.time_end:
                        the_day = start_day.strftime('%d-%m-%Y') + ','
                        if the_day[3:4] == '0':
                            the_day = the_day[:3] + the_day[4:]
                        string += the_day
                start_day += timedelta(days=1)
    return string[:len(string)-1]


@api_view(['GET'])
def getClosedWeekDaysFromRestaurant(request, id):
    closed_days_of_the_week = return_weekdays_not_open(id)
    return JsonResponse(closed_days_of_the_week, safe=False)

@api_view(['POST'])
def getShifts(request):
    data = request.data
    id = data['id']
    choosenday = data['date']
    choosenday = choosenday[:10]
    choosenday = datetime.strptime(choosenday, '%Y-%m-%d')
    choosenday = choosenday.strftime("%Y-%m-%d")
    choosenday = datetime.strptime(choosenday, '%Y-%m-%d')
    weekday = numbers_to_weekday(choosenday.isoweekday())
    print('choosenday')
    print(choosenday)
    print('choosenday.isoweekday()')
    print(choosenday.isoweekday())
    print('weekday')
    print(weekday)
    openDays = return_correct_weekday_filter(id,weekday)
    print(openDays)
    print('openDays')
    list = []
    for x in openDays:
        if x.shift == 'Breakfast' and 'Breakfast' not in list:
            list.append('Breakfast')
        if x.shift == 'Lunch' and 'Lunch' not in list:
            list.append('Lunch')
        if x.shift == 'Dinner' and 'Dinner' not in list:
            list.append('Dinner')

    zones = placeOfTable.objects.filter(restaurant__pk__exact=id)
    zone_list = []
    for y in zones:
        zone_list.append(y.place_of_table)
    dictionarie = {}
    dictionarie['shifts'] = list
    dictionarie['zones'] = zone_list
    print('dictionariessssssssssssssssssssssssssssssssss')
    print(dictionarie)
    return Response(dictionarie)

@api_view(['GET'])
def getClosedExceptionsDaysFromRestaurant(request, id):
    closedExceptionsDays = returnStringOfClosedExceptions(id)
    return JsonResponse(closedExceptionsDays, safe=False)

@api_view(['POST'])
def getAvailableTimes(request):
    print('start here')
    data = request.data
    id = data['id']
    choosenday = data['date']
    numberOfPeople = data['numberOfPeople']
    shift = data['shift']
    placeOfTables = data['placeOfTable']
    restaurant = restaurants.objects.get(pk__exact=id)
    time_divider = restaurant.each_time
    choosenday = choosenday[:10]
    choosenday = datetime.strptime(choosenday, '%Y-%m-%d')
    choosenday = choosenday.strftime("%Y-%m-%d")
    choosenday = datetime.strptime(choosenday, '%Y-%m-%d')
    weekday = numbers_to_weekday(choosenday.isoweekday())
    reservation = reservations.objects.filter(date__exact=choosenday)
    weekfilter = return_correct_weekday_filter(id,weekday)
    tu = retrieveTablesUsed(choosenday, shift, id, placeOfTables)
    time_divider_list = time_divider.split(":")
    weekfilter = return_correct_weekday_filter_w_shift(id,weekday,shift)
    hours_list = []
    print('xy1')
    print('weekfilter')
    print(weekfilter)
    print('reservation')
    print(reservation)
    for y in weekfilter:
        starttime = y.start_time
        endtime = y.end_time
        starttime = timedelta(hours=starttime.hour, minutes=starttime.minute, seconds=starttime.second, microseconds=starttime.microsecond)
        endtime = timedelta(hours=endtime.hour, minutes=endtime.minute, seconds=endtime.second, microseconds=endtime.microsecond)
        print('xy')
        while starttime < endtime:
            people = 0
            add_hour = True
            
            for xy in reservation:
                print('xy')
                print(xy)
                print('starttime')
                print(starttime)
                print('xy.time')
                print(xy.time + ':00')
                verify_time = xy.time + ':00'
                if str(starttime) == str(verify_time):
                    people += xy.number_of_people
                    print('people')
                    print(people)
                    print('restaurant.accept_people_per_each_time')
                    print(restaurant.accept_people_per_each_time)
                    if restaurant.accept_people_per_each_time  < people:
                        add_hour = False
            if add_hour == True:
                hours_list.append(str(starttime))
            starttime = starttime + timedelta(hours=int(time_divider_list[0]),minutes=int(time_divider_list[1]))
    estimated_time = return_estimated_time(int(numberOfPeople), id)
    open_time = retrieveAvailableHoursToReservation(tu, int(numberOfPeople), estimated_time, id, hours_list, placeOfTables)
    zones = placeOfTable.objects.filter(restaurant__pk__exact=id)
    xi = 0
    xii = 0
    open_time_save = []
    save_zone = ''
    zone_list = []
    zone_dic = {}
    remove_first_item = open_time.pop(0)
    sorted_hours = sorted(open_time)
    print(open_time)
    print('open_time')
    for y in zones:
        zone_list.append(y.place_of_table)
    """     
    while zone_list:
        current_zone = zone_list.pop(0)
        zone_dic[current_zone] = {'zone_name': current_zone, 'time_list': []}

        open_times_to_remove = []
        for ot in open_time:
            if ot == current_zone:
                open_times_to_remove.append(ot)
            elif is_valid_time(ot) and ot not in zone_dic[current_zone]['time_list']:
                zone_dic[current_zone]['time_list'].append(ot)

        open_time = [ot for ot in open_time if ot not in open_times_to_remove]

    # Sort time_list for each zone
    for zone in zone_dic:
        zone_dic[zone]['time_list'] = sorted(zone_dic[zone]['time_list'])
            
    print(zone_dic) 
    """
    '''
    for x in open_time:
        yi = 0
        for y in range(0,len(zone_list),1):
            if open_time[xi] == zone_list[yi]:

                save_zone = '  /  ' + zone_list[yi]
                zone_list.remove(zone_list[yi])
                yi -= 1
            yi += 1
        if save_zone != '':
            if open_time[xi] != save_zone[5:]:
                open_time_save.append(open_time[xi])
                open_time_save[xii] +=  save_zone
            else:
                xii -= 1
            xii += 1
        xi += 1 
        '''

    choosenday =  choosenday.strftime("%m/%d/%Y")
    return JsonResponse(sorted_hours, safe=False)

@api_view(['POST'])
def createReservation(request):
    data = request.data
    id = data['id']
    choosenday = data['date']
    choosenday = choosenday[:10]
    choosenday = datetime.strptime(choosenday, '%Y-%m-%d')
    number_of_people = data['numberOfPeople']
    shift = data['shift']
    time = data['time']
    placeOfTables = data['placeOfTables']
    hours_list = time[:5]
    time_to_sum_one = hours_list + ':00'
    time_to_sum_one = datetime.strptime(time_to_sum_one, '%H:%M:%S')
    estimated_time = return_estimated_time(int(number_of_people), id)
    estimated_time_list = estimated_time.split(":")
    estimated_time_list = time_to_sum_one + timedelta(hours=int(estimated_time_list[0]),minutes=int(estimated_time_list[1]))
    estimated_time_list = estimated_time_list.strftime("%H:%M:%S")
    estimated_time_list = estimated_time_list[:5]
    place_of_table_of_time = time[13:]
    list_hours = []
    list_hours.append(hours_list + ':00')
    zone = time[13:]
    tu = retrieveTablesUsed(choosenday, shift, id, placeOfTables)
    assign_tables = assignThTables(tu, int(number_of_people), estimated_time, id, list_hours, placeOfTables)
    table_list = ''
    for ii in assign_tables:
        table_list += ii + ','
    table_list = table_list[:-1]
    restaurant = restaurants.objects.get(pk__exact=id)
    print('place_of_table_of_time')
    print(place_of_table_of_time)
    table_place_instance = placeOfTable.objects.get(restaurant__pk__exact=id, place_of_table__contains=data['placeOfTables'])
    print('error here')
    choosenday = choosenday.strftime("%Y-%m-%d")

    try:
        print('error here')
        reservation = reservations.objects.create(
            restaurant = restaurant,
            full_name=data['name'],
            email=data['email'],
            phone_number=data['phone_number'],
            date=choosenday,
            shift = shift,
            number_of_people = int(data['numberOfPeople']),
            time = hours_list,
            estimatedtime=estimated_time_list,
            tablesused = table_list,
            message = data['message'],
            baby_chair = int(data['baby_chair']),
            table_place_preference = table_place_instance,
            status = 'Pending_from_customer',
            token = str(uuid.uuid4()),
        )
        print('error here')
        reservation.save()

        token = reservation.token

        link_to_reservation_menu = 'http://localhost:3000/customer_reservation_menu/' + str(token) + '/confirm'

        template = loader.get_template('contact_form.txt')
        email_context = {
            'name':data['name'],
            'email':data['email'],
            'day':choosenday,
            'time':hours_list,
            'shift':shift,
            'restaurant':restaurant.restaurant_name,
            'phone_number':int(data['numberOfPeople']),
            'link_to_reservation_menu':link_to_reservation_menu,
        }
        message = template.render(email_context)
        email_forclient = EmailMultiAlternatives (
            restaurant.restaurant_name, message,
            'jhonnykellerdev@gmail.com',
            [data['email']],
        )

        # Convert the html and css inside the [contact_form.txt] to HTML templete
        email_forclient.content_subtype = 'html'
        email_forclient.send()
        
        send_sms(data['phone_number'], ' Acesse a sua reserva do {}, no seguinte link para confirmar a sua reserva, também pode cancelar ou editar a sua reserva em http://localhost:3000/{}'.format(restaurant.restaurant_name,token)) 
        

        serializer = ReservationsSerializer(reservation, many=False)
        return Response(serializer.data)
    except Exception as e:
        message = {'detail': f'There was a problem with the reservation: {str(e)}'}
        return Response(message, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
def cancelReservation(request, token):
    try:
        reservation = reservations.objects.get(token=token)
        reservation.status = "Cancelled"
        print(reservation)
        reservation.save()
        restaurant = restaurants.objects.get(restaurant_name=reservation.restaurant)

        template = loader.get_template('cancelled_reservation_from_restaurant.txt')
        print('reservation.email')
        print(reservation.email)
        email_context = {
            'name':reservation.full_name,
            'email':reservation.email,
            'day':reservation.date,
            'time':reservation.time,
            'shift':reservation.shift,
            'restaurant':restaurant.restaurant_name,
            'phone_number':reservation.phone_number,
        }
        message = template.render(email_context)
        email_forclient = EmailMultiAlternatives (
            restaurant.restaurant_name, message,
            'jhonnykellerdev@gmail.com',
            [reservation.email],
        )
        # Convert the html and css inside the [contact_form.txt] to HTML templete
        email_forclient.content_subtype = 'html'
        email_forclient.send()
        return Response({"success": True, "message": "Reserva cancelada."}, status=status.HTTP_200_OK)
    except reservations.DoesNotExist:
        return Response({"success": False, "message": "Reserva não encontrada."}, status=status.HTTP_404_NOT_FOUND)    
        


@api_view(['POST'])
def editReservation(request, token):
    data = request.data
    id = data['id']
    choosenday = data['date']
    choosenday = choosenday[:10]
    choosenday = datetime.strptime(choosenday, '%Y-%m-%d')
    number_of_people = data['numberOfPeople']
    shift = data['shift']
    time = data['time']
    placeOfTables = data['placeOfTables']
    hours_list = time[:5]
    time_to_sum_one = hours_list + ':00'
    time_to_sum_one = datetime.strptime(time_to_sum_one, '%H:%M:%S')
    estimated_time = return_estimated_time(int(number_of_people), id)
    estimated_time_list = estimated_time.split(":")
    estimated_time_list = time_to_sum_one + timedelta(hours=int(estimated_time_list[0]),minutes=int(estimated_time_list[1]))
    estimated_time_list = estimated_time_list.strftime("%H:%M:%S")
    estimated_time_list = estimated_time_list[:5]
    place_of_table_of_time = time[11:]
    
    list_hours = []
    list_hours.append(hours_list + ':00')
    zone = time[13:]
    tu = retrieveTablesUsed(choosenday, shift, id, placeOfTables)
    assign_tables = assignThTables(tu, int(number_of_people), estimated_time, id, list_hours, zone)
    table_list = ''
    for ii in assign_tables:
        table_list += ii + ','
    table_list = table_list[:-1]
    restaurant = restaurants.objects.get(pk__exact=id)
    choosenday = choosenday.strftime("%Y-%m-%d")
    print('place_of_table_of_time')
    print(place_of_table_of_time)
    table_place_instance = placeOfTable.objects.get(restaurant__pk__exact=id, place_of_table__contains=place_of_table_of_time)
    
    try:
        reservation = reservations.objects.get(token=token)
        print('he2')
        reservation = reservations.objects.get(token=token)
        reservation.restaurant = restaurant
        reservation.full_name = data['name']
        reservation.email = data['email']
        reservation.phone_number = data['phone_number']
        reservation.date = choosenday
        reservation.shift = shift
        reservation.number_of_people = int(data['numberOfPeople'])
        reservation.time = hours_list
        reservation.estimatedtime = estimated_time_list
        reservation.tablesused = table_list
        reservation.message = data['message']
        reservation.baby_chair = int(data['baby_chair'])
        reservation.table_place_preference = table_place_instance
        reservation.status = 'Edited'
        reservation.save()
        print('here2')
        message = {'detail': 'Reserva editada'}
        serializer = ReservationsSerializer(reservation, many=False)
        send_sms(data['phone_number'], 'Your reservation was Edited and you can acess it here http://localhost:3000/{}'.format(token))
        print('here3')
        return Response(serializer.data)
    except Exception as e:
        message = {'detail': f'There was a problem with the reservation: {str(e)}'}
        return Response(message, status=status.HTTP_400_BAD_REQUEST)
    
class reservationCustomersMenu(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = ReservationsSerializer
    lookup_field = 'token'

    def get_queryset(self):
        token = self.kwargs.get('token')
        queryset = reservations.objects.filter(token=token)
        return queryset

    def get(self, request, *args, **kwargs):
        confirm_or_not = self.kwargs.get('confirm_or_not')
        reservation_instance = self.get_object()

        if confirm_or_not == 'confirm':
            if reservation_instance.status == 'Pending_from_customer':
                if reservation_instance.number_of_people <= reservation_instance.restaurant.auto_accept_limit:
                    reservation_instance.status = 'Accepted'
                    link_to_reservation_menu = 'http://localhost:3000/customer_reservation_menu/' + str(reservation_instance.token) + '/accepted'
                    template = loader.get_template('accepted_reservation.txt')
                    email_context = {
                        'name':reservation_instance.full_name,
                        'email':reservation_instance.email,
                        'day':reservation_instance.date,
                        'time':reservation_instance.time,
                        'shift':reservation_instance.shift,
                        'restaurant':reservation_instance.restaurant.restaurant_name,
                        'phone_number':reservation_instance.phone_number,
                        'link_to_reservation_menu':link_to_reservation_menu,
                    }
                    message = template.render(email_context)
                    email_forclient = EmailMultiAlternatives (
                        reservation_instance.restaurant.restaurant_name, message,
                        'jhonnykellerdev@gmail.com',
                        [reservation_instance.email],
                    )
                    # Convert the html and css inside the [contact_form.txt] to HTML templete
                    email_forclient.content_subtype = 'html'
                    email_forclient.send()
                else:
                    reservation_instance.status = 'Pending_from_restaurant'
                reservation_instance.save()

        serializer = self.get_serializer(reservation_instance)
        return Response(serializer.data)
    
@api_view(['GET'])
def restaurant_reservation_limits(request, restaurant_id):
    try:
        restaurant = restaurants.objects.get(pk=restaurant_id)
    except restaurants.DoesNotExist:
        return Response({'error': 'Restaurant not found'}, status=404)

    serializer = RestaurantsSerializer(restaurant)
    limit_people_reservation = serializer.data['limit_people_reservation']
    limit_baby_chairs_reservation = serializer.data['limit_baby_chairs_reservation']

    reservation_numbers = list(range(1, limit_people_reservation + 1))
    baby_chair_numbers = list(range(1, limit_baby_chairs_reservation + 1))

    return Response({'reservation_numbers': reservation_numbers, 'baby_chair_numbers': baby_chair_numbers})
