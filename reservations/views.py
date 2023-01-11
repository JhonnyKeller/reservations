from django.shortcuts import render
from restaurants.models import (restaurants,tables,restaurantOpenDaysOfTheWeek,
                                estimatedTimeCustomersSpend,closedExceptions,
                                placeOfTable,timeDivider,numberOfPeopleWhenTablesConnect)
from reservations.forms import reservationsForm
from reservations.models import reservations
from datetime import datetime
from django.http import JsonResponse
from datetime import datetime, timedelta
from .assign_tables_function import assignThTables


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

def retrieveAvailableHoursToReservation(tables_used, necessary_people, estimated_time, restaurant_name, hours_list):
    connect_logic = numberOfPeopleWhenTablesConnect.objects.filter(restaurant__restaurant_name__contains=restaurant_name)
    restaurant_tables = tables.objects.filter(restaurant__restaurant_name__contains=restaurant_name)
    zones = placeOfTable.objects.filter(restaurant__restaurant_name__contains=restaurant_name)
    availabletimes = []
    for x in zones:
        tables_zone = tables.objects.filter(restaurant__restaurant_name__contains=restaurant_name,place_of_table__pk__contains=x.pk)
        availabletimes.append(x.place_of_table)
        the_hours = hours_list[:]
        print('------------------zone---------------------')
        print(x)
        for y in tables_zone:
            print('------------------Current table---------------------')
            print(y)
            print(the_hours)
            ii = -1
            for hours_saved in range(0,len(the_hours),1):
                ii += 1
                save_necessary_people = necessary_people
                temporary_table = []
                used_table_list = []
                for i in range(0, len(tables_used), 3):
                    if int(tables_used[i])  == int(y.table_number):
                        temporary_table.append(tables_used[i])
                        temporary_table.append(tables_used[i+1])
                        temporary_table.append(tables_used[i+2])
                verify_hour = False
                temporary_table_two = []
                if temporary_table != []:
                    for tt in range(0,len(temporary_table),3):
                        verify_hour = verify_hour_availability(the_hours[ii],temporary_table[tt+1],temporary_table[tt+2],estimated_time)
                        if verify_hour == False:
                            break
                if verify_hour or temporary_table == []:
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
                        break
                    can_connect_list = y.can_connect_tables[:]
                    can_connect_list = can_connect_list.split(',')
                    for utl in range(0, len(used_table_list), 1):
                        for ccll in can_connect_list:
                            if ccll == utl:
                                can_connect_list.remove(used_table_list[utl])
                    for ccl_two in range(0,len(can_connect_list),1):
                        if ii == -1:
                            break
                        for i in range(0, len(tables_used), 3):
                            if int(tables_used[i])  == int(can_connect_list[ccl_two]):
                                temporary_table_two.append(tables_used[i])
                                temporary_table_two.append(tables_used[i+1])
                                temporary_table_two.append(tables_used[i+2])
                        verify_hour = False
                        temporary_table_three = []
                        if temporary_table_two != []:
                            for tt in range(0,len(temporary_table_two),3):
                                verify_hour = verify_hour_availability(the_hours[ii],temporary_table_two[tt+1],temporary_table_two[tt+2],estimated_time)
                                if verify_hour == False:
                                    break
                        if verify_hour or temporary_table_two == []:
                            check_table = tables.objects.filter(table_number__contains=can_connect_list[ccl_two])
                            save_necessary_people_two = save_necessary_people_one
                            save_necessary_people_two -= int(check_table[0].number_of_seats) + connect_logic[0].number_of_chairs
                            used_table_list_one = used_table_list
                            used_table_list_one.append(can_connect_list[ccl_two])
                            if save_necessary_people_two <= 0:
                                availabletimes.append(the_hours[ii])
                                the_hours.remove(the_hours[ii])
                                ii -= 1
                                break
                            can_connect_list_two = check_table[0].can_connect_tables[:]
                            can_connect_list_two = can_connect_list_two.split(',')
                            for utl in range(0, len(used_table_list_one), 1):
                                for ccll in can_connect_list_two:
                                    if ccll == used_table_list_one[utl]:
                                        can_connect_list_two.remove(used_table_list_one[utl])
                            for ccl_three in range(0,len(can_connect_list_two),1):
                                if ii == -1:
                                    break
                                for i in range(0, len(tables_used), 3):
                                    if int(tables_used[i]) == int(can_connect_list_two[ccl_three]):
                                        temporary_table_three.append(tables_used[i])
                                        temporary_table_three.append(tables_used[i+1])
                                        temporary_table_three.append(tables_used[i+2])
                                verify_hour = False
                                temporary_table_four = []
                                if temporary_table_three != []:
                                    for tt in range(0,len(temporary_table_three),3):
                                        verify_hour = verify_hour_availability(the_hours[ii],temporary_table_three[tt+1],temporary_table_three[tt+2],estimated_time)
                                        if verify_hour == False:
                                            break
                                if verify_hour or temporary_table_three == []:
                                    check_table = tables.objects.filter(table_number__contains=can_connect_list_two[ccl_three])
                                    save_necessary_people_three = save_necessary_people_two
                                    save_necessary_people_three -= int(check_table[0].number_of_seats) + connect_logic[1].number_of_chairs
                                    used_table_list_two = used_table_list_one
                                    used_table_list_two.append(can_connect_list_two[ccl_three])
                                    if save_necessary_people_three <= 0:
                                        availabletimes.append(the_hours[ii])
                                        the_hours.remove(the_hours[ii])
                                        ii -= 1
                                        break
                                    can_connect_list_three = check_table[0].can_connect_tables[:]
                                    can_connect_list_three = can_connect_list_three.split(',')
                                    for utl in range(0, len(used_table_list_two), 1):
                                        for ccll in can_connect_list_three:
                                            if ccll == used_table_list_two[utl]:
                                                can_connect_list_three.remove(used_table_list_two[utl])
                                    for ccl_four in range(0,len(can_connect_list_three),1):
                                        if ii == -1:
                                            break
                                        for i in range(0, len(tables_used), 3):
                                            if int(tables_used[i]) == int(can_connect_list_three[ccl_four]):
                                                temporary_table_four.append(tables_used[i])
                                                temporary_table_four.append(tables_used[i+1])
                                                temporary_table_four.append(tables_used[i+2])
                                        verify_hour = False
                                        temporary_table_five = []
                                        if temporary_table_four != []:
                                            for tt in range(0,len(temporary_table_four),3):
                                                verify_hour = verify_hour_availability(the_hours[ii],temporary_table_four[tt+1],temporary_table_four[tt+2],estimated_time)
                                                if verify_hour == False:
                                                    break
                                        if verify_hour or temporary_table_four == []:
                                            check_table = tables.objects.filter(table_number__contains=can_connect_list_three[ccl_four])
                                            save_necessary_people_four = save_necessary_people_three
                                            save_necessary_people_four -= int(check_table[0].number_of_seats) + connect_logic[2].number_of_chairs
                                            used_table_list_three = used_table_list_two
                                            used_table_list_three.append(can_connect_list_three[ccl_four])
                                            if save_necessary_people_four <= 0:
                                                availabletimes.append(the_hours[ii])
                                                the_hours.remove(the_hours[ii])
                                                ii -= 1
                                                break
                                            can_connect_list_four = check_table[0].can_connect_tables[:]
                                            can_connect_list_four = can_connect_list_four.split(',')
                                            for utl in range(0, len(used_table_list_three), 1):
                                                for ccll in can_connect_list_four:
                                                    if ccll == used_table_list_three[utl]:
                                                        can_connect_list_four.remove(used_table_list_three[utl])
                                            for ccl_five in range(0,len(can_connect_list_four),1):
                                                if ii == -1:
                                                    break
                                                for i in range(0, len(tables_used), 3):
                                                    if int(tables_used[i]) == int(can_connect_list_four[ccl_five]):
                                                        temporary_table_five.append(tables_used[i])
                                                        temporary_table_five.append(tables_used[i+1])
                                                        temporary_table_five.append(tables_used[i+2])
                                                verify_hour = False
                                                temporary_table_six = []
                                                if temporary_table_five != []:
                                                    for tt in range(0,len(temporary_table_five),3):
                                                        verify_hour = verify_hour_availability(the_hours[ii],temporary_table_five[tt+1],temporary_table_five[tt+2],estimated_time)
                                                        if verify_hour == False:
                                                            break
                                                if verify_hour or temporary_table_five == []:
                                                    check_table = tables.objects.filter(table_number__contains=can_connect_list_four[ccl_five])
                                                    save_necessary_people_five = save_necessary_people_four
                                                    save_necessary_people_five -= int(check_table[0].number_of_seats) + connect_logic[1].number_of_chairs
                                                    used_table_list_four = used_table_list_three
                                                    used_table_list_four.append(can_connect_list_four[ccl_five])
                                                    if save_necessary_people_five <= 0:
                                                        print(ii)
                                                        availabletimes.append(the_hours[ii])
                                                        the_hours.remove(the_hours[ii])
                                                        ii -= 1
                                                        break
                                                    can_connect_list_five = check_table[0].can_connect_tables[:]
                                                    can_connect_list_five = can_connect_list_five.split(',')
                                                    for utl in range(0, len(used_table_list_four), 1):
                                                        for ccll in can_connect_list_five:
                                                            if ccll == used_table_list_four[utl]:
                                                                can_connect_list_five.remove(used_table_list_four[utl])
                                                    for ccl_six in range(0,len(can_connect_list_five),1):
                                                        if ii == -1:
                                                            break
                                                        for i in range(0, len(tables_used), 3):
                                                            if int(tables_used[i]) == int(can_connect_list_five[ccl_six]):
                                                                temporary_table_six.append(tables_used[i])
                                                                temporary_table_six.append(tables_used[i+1])
                                                                temporary_table_six.append(tables_used[i+2])
                                                        verify_hour = False
                                                        temporary_table_seven = []
                                                        if temporary_table_six != []:
                                                            for tt in range(0,len(temporary_table_six),3):
                                                                verify_hour = verify_hour_availability(the_hours[ii],temporary_table_six[tt+1],temporary_table_six[tt+2],estimated_time)
                                                                if verify_hour == False:
                                                                    break
                                                        if verify_hour or temporary_table_six == []:
                                                            check_table = tables.objects.filter(table_number__contains=can_connect_list_five[ccl_six])
                                                            save_necessary_people_six = save_necessary_people_five
                                                            save_necessary_people_six -= int(check_table[0].number_of_seats) + connect_logic[2].number_of_chairs
                                                            used_table_list_five = used_table_list_four
                                                            used_table_list_five.append(can_connect_list_five[ccl_six])
                                                            if save_necessary_people_six <= 0:
                                                                print(ii)
                                                                print(the_hours)
                                                                availabletimes.append(the_hours[ii])
                                                                the_hours.remove(the_hours[ii])
                                                                ii -= 1
                                                                break
                                                            can_connect_list_six = check_table[0].can_connect_tables[:]
                                                            can_connect_list_six = can_connect_list_six.split(',')
                                                            for utl in range(0, len(used_table_list_five), 1):
                                                                for ccll in can_connect_list_six:
                                                                    if ccll == used_table_list_five[utl]:
                                                                        can_connect_list_six.remove(used_table_list_five[utl])


    return availabletimes


def retrieveTablesUsed(date, shift, restaurantname):
    print(date)
    print(shift)
    print(restaurantname)
    reservation = reservations.objects.filter(restaurant__restaurant_name__contains=restaurantname,
                                              date__exact=date,shift__contains=shift)
    print(reservation)
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

def return_correct_weekday_filter(restaurant,weekday):
    filter = []
    if weekday == 'Monday':
        filter = restaurantOpenDaysOfTheWeek.objects.filter(restaurant__restaurant_name__contains=restaurant,Monday=True)
        print('m')
    if weekday == 'Tuesday':
        filter = restaurantOpenDaysOfTheWeek.objects.filter(restaurant__restaurant_name__contains=restaurant,Tuesday=True)
        print('m')
    if weekday == 'Wednesday':
        filter = restaurantOpenDaysOfTheWeek.objects.filter(restaurant__restaurant_name__contains=restaurant,Wednesday=True)
        print('m')
    if weekday == 'Thursday':
        filter = restaurantOpenDaysOfTheWeek.objects.filter(restaurant__restaurant_name__contains=restaurant,Thursday=True)
        print('m')
    if weekday == 'Friday':
        filter = restaurantOpenDaysOfTheWeek.objects.filter(restaurant__restaurant_name__contains=restaurant,Friday=True)
        print('m')
    if weekday == 'Saturday':
        filter = restaurantOpenDaysOfTheWeek.objects.filter(restaurant__restaurant_name__contains=restaurant,Saturday=True)
        print('m')
    if weekday == 'Sunday':
        filter = restaurantOpenDaysOfTheWeek.objects.filter(restaurant__restaurant_name__contains=restaurant,Sunday=True)
        print(filter)
    return filter

def return_correct_weekday_filter_w_shift(restaurant,weekday,shift):
    filter = []
    if weekday == 'Monday':
        filter = restaurantOpenDaysOfTheWeek.objects.filter(restaurant__restaurant_name__contains=restaurant,Monday=True,shift__contains=shift)
        print('m')
    if weekday == 'Tuesday':
        filter = restaurantOpenDaysOfTheWeek.objects.filter(restaurant__restaurant_name__contains=restaurant,Tuesday=True,shift__contains=shift)
        print('m')
    if weekday == 'Wednesday':
        filter = restaurantOpenDaysOfTheWeek.objects.filter(restaurant__restaurant_name__contains=restaurant,Wednesday=True,shift__contains=shift)
        print('m')
    if weekday == 'Thursday':
        filter = restaurantOpenDaysOfTheWeek.objects.filter(restaurant__restaurant_name__contains=restaurant,Thursday=True,shift__contains=shift)
        print('m')
    if weekday == 'Friday':
        filter = restaurantOpenDaysOfTheWeek.objects.filter(restaurant__restaurant_name__contains=restaurant,Friday=True,shift__contains=shift)
        print('m')
    if weekday == 'Saturday':
        filter = restaurantOpenDaysOfTheWeek.objects.filter(restaurant__restaurant_name__contains=restaurant,Saturday=True,shift__contains=shift)
        print('m')
    if weekday == 'Sunday':
        filter = restaurantOpenDaysOfTheWeek.objects.filter(restaurant__restaurant_name__contains=restaurant,Sunday=True,shift__contains=shift)
        print('m')
    return filter

def checkIfThereIsWeekDay(weekday, value, restaurant):
    weekday = return_correct_weekday_filter(restaurant,weekday)
    if weekday.count() <= 0:
        return value
    return None

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

def return_estimated_time(number_of_people):
    estimated_time = estimatedTimeCustomersSpend.objects.filter(number_of_people__gte=number_of_people)
    if estimated_time.count() <= 0:
        estimated_time = estimatedTimeCustomersSpend.objects.filter(number_of_people__lte=number_of_people)
        estimative = estimated_time[estimated_time.count()-1].estimated_time
    else:
        estimative = estimated_time[0].estimated_time
    estimative = estimative.strftime("%H:%M")
    return estimative

def returnStringOfClosedExceptions(restaurant):
    closed_days = closedExceptions.objects.filter(restaurant__restaurant_name__contains=restaurant)
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
                filter_weekday = return_correct_weekday_filter(restaurant,numbers_to_weekday(start_day.isoweekday()))
                for y in filter_weekday:
                    if lowest_start_time == '':
                        lowest_start_time = y.start_time
                        print('lowest_start_time')
                        print(lowest_start_time)
                    elif lowest_start_time > y.start_time:
                        lowest_start_time = y.start_time
                    if higher_end_time == '':
                        higher_end_time = y.end_time
                    elif higher_end_time < y.end_time:
                        higher_end_time = y.end_time
                if lowest_start_time != '':
                    print('times')
                    print(lowest_start_time)
                    print(x.time_start)
                    if lowest_start_time >= x.time_start and higher_end_time <= x.time_end:
                        the_day = start_day.strftime('%d-%m-%Y') + ','
                        if the_day[3:4] == '0':
                            the_day = the_day[:3] + the_day[4:]
                        print('the_day[3:4]')
                        print(the_day[3:4])
                        string += the_day
                start_day += timedelta(days=1)
    return string[:len(string)-1]


# Create your views here.
def reservationss(request, username, restaurantname):
    closed_days = returnStringOfClosedExceptions(restaurantname)
    print('closed_days')
    print(closed_days)
    stage = request.POST.get('stage', '1')
    number_of_people = request.POST.get('number_of_people', 'False')
    shift = request.POST.get('shift', 'False')
    baby_chair = request.POST.get('baby_chair', 'False')
    full_name = request.POST.get('full_name','')
    email = request.POST.get('email','')
    phone_number = request.POST.get('phone_number','')
    choosenday = request.POST.get('choosenday','')
    message = request.POST.get('message','')
    time = request.POST.get('time','')
    open_time_save = request.POST.get('open_time_save','')
    form_saved = 'False'
    time_divider_list = []
    today = datetime.now()
    # choosenday = datetime.strptime(today, '%m/%d/%Y')
    choosen_day =  today.strftime("%m/%d/%Y")
    form = reservationsForm()
    weekdaysnotopen = return_weekdays_not_open(restaurantname)
    print('weekdaysnotopen')
    print(weekdaysnotopen)
    closed_exceptions = closedExceptions.objects.filter(restaurant__restaurant_name__contains=restaurantname)
    restaurant = restaurants.objects.filter(owner__username__contains=username,
                                            restaurant_name__contains=restaurantname)


    if request.method == 'POST':
        if stage == '2':

            choosenday = datetime.strptime(choosenday, '%m/%d/%Y')
            choosenday = choosenday.strftime("%Y-%m-%d")
            choosenday = datetime.strptime(choosenday, '%Y-%m-%d')
            weekday = numbers_to_weekday(choosenday.isoweekday())
            reservation = reservations.objects.filter(date__contains=choosenday)
            weekfilter = return_correct_weekday_filter(restaurantname,weekday)
            tu = retrieveTablesUsed(choosenday, shift, restaurantname)
            time_divider = timeDivider.objects.filter(restaurant__restaurant_name__contains=restaurantname)
            time_divider = time_divider[0].each_time
            time_divider_list = time_divider.split(":")
            weekfilter = return_correct_weekday_filter_w_shift(restaurantname,weekday,shift)
            hours_list = []
            for y in weekfilter:
                starttime = y.start_time
                endtime = y.end_time
                starttime = timedelta(hours=starttime.hour, minutes=starttime.minute, seconds=starttime.second, microseconds=starttime.microsecond)
                endtime = timedelta(hours=endtime.hour, minutes=endtime.minute, seconds=endtime.second, microseconds=endtime.microsecond)
                while starttime < endtime:
                    hours_list.append(str(starttime))
                    starttime = starttime + timedelta(hours=int(time_divider_list[0]),minutes=int(time_divider_list[1]))
            estimated_time = return_estimated_time(int(number_of_people))
            open_time = retrieveAvailableHoursToReservation(tu, int(number_of_people), estimated_time, restaurantname, hours_list)
            zones = placeOfTable.objects.filter(restaurant__restaurant_name__contains=restaurantname)
            xi = 0
            xii = 0
            open_time_save = []
            save_zone = ''
            zone_list = []
            for y in zones:
                zone_list.append(y.place_of_table)
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
            choosenday =  choosenday.strftime("%m/%d/%Y")

        if stage == '4':
            choosenday = datetime.strptime(choosenday, '%m/%d/%Y')
            weekday = numbers_to_weekday(choosenday.isoweekday())
            reservation = reservations.objects.filter(date__contains=choosenday)
            weekfilter = return_correct_weekday_filter(restaurantname,weekday)
            tu = retrieveTablesUsed(choosenday, shift, restaurantname)
            time_divider = timeDivider.objects.filter(restaurant__restaurant_name__contains=restaurantname)
            time_divider = time_divider[0].each_time
            time_divider_list = time_divider.split(":")
            weekfilter = return_correct_weekday_filter_w_shift(restaurantname,weekday,shift)
            hours_list = []
            for y in weekfilter:
                starttime = y.start_time
                endtime = y.end_time
                starttime = timedelta(hours=starttime.hour, minutes=starttime.minute, seconds=starttime.second, microseconds=starttime.microsecond)
                endtime = timedelta(hours=endtime.hour, minutes=endtime.minute, seconds=endtime.second, microseconds=endtime.microsecond)
                while starttime < endtime:
                    hours_list.append(str(starttime))
                    starttime = starttime + timedelta(hours=int(time_divider_list[0]),minutes=int(time_divider_list[1]))
            estimated_time = return_estimated_time(int(number_of_people))
            zones =placeOfTable.objects.filter(restaurant__restaurant_name__contains=restaurantname)
            open_time = retrieveAvailableHoursToReservation(tu, int(number_of_people), estimated_time, restaurantname, hours_list)
            hours_list = time[:5]
            time_to_sum_one = hours_list + ':00'
            time_to_sum_one = datetime.strptime(time_to_sum_one, '%H:%M:%S')

            estimated_time = estimated_time.split(":")
            estimated_time = time_to_sum_one + timedelta(hours=int(estimated_time[0]),minutes=int(estimated_time[1]))
            estimated_time = estimated_time.strftime("%H:%M:%S")
            estimated_time = estimated_time[:5]

            place_of_table_of_time = time[13:]
            list_hours = []
            list_hours.append(hours_list)
            zone = time[13:]
            assign_tables = assignThTables(tu, int(number_of_people), estimated_time, restaurantname, list_hours, zone)
            table_list = ''
            for ii in assign_tables:
                table_list += ii + ','
            table_list = table_list[:-1]
            choosenday = choosenday.strftime("%Y-%m-%d")
            form = reservationsForm(request.POST)
            if form.is_valid():
                saveform = form.save(commit=False)
                saveform.restaurant = restaurant = restaurants.objects.get(owner__username__contains=username,
                                                        restaurant_name__contains=restaurantname)
                saveform.tablesused = table_list
                saveform.time = hours_list
                saveform.estimatedtime = estimated_time
                instance = placeOfTable.objects.get(restaurant__restaurant_name__contains=restaurantname,place_of_table__contains=place_of_table_of_time)
                saveform.table_place_preference = instance
                saveform.date = choosenday
                saveform.save()
                form_saved = 'True'


    return render(request,'reservations/reservation.html',{'restaurantname':restaurantname,
                                                        'stage':stage,
                                                        'weekdaysnotopen':weekdaysnotopen,
                                                        'choosenday':choosenday,
                                                        'message':message,
                                                        'choosen_day':choosen_day,
                                                        'phone_number':phone_number,
                                                        'form':form,
                                                        'open_time_save':open_time_save,
                                                        'time':time,
                                                        'number_of_people':number_of_people,
                                                        'shift':shift,'baby_chair':baby_chair,
                                                        'form_saved':form_saved,
                                                        'closed_days':closed_days})
