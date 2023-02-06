from django.shortcuts import render
from restaurants.models import (restaurants,tables,restaurantOpenDaysOfTheWeek,
                                estimatedTimeCustomersSpend,closedExceptions,
                                placeOfTable,timeDivider,numberOfPeopleWhenTablesConnect)
from reservations.forms import reservationsForm
from reservations.models import reservations
from datetime import datetime
from django.http import JsonResponse
from datetime import datetime, timedelta


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

def assignThTables(tables_used, necessary_people, estimated_time, restaurant_name, hours_list, zone):
    connect_logic = numberOfPeopleWhenTablesConnect.objects.filter(restaurant__restaurant_name__contains=restaurant_name)
    restaurant_tables = tables.objects.filter(restaurant__restaurant_name__contains=restaurant_name)
    zones = placeOfTable.objects.filter(restaurant__restaurant_name__contains=restaurant_name,place_of_table__contains=zone)
    availabletimes = []
    for x in zones:
        tables_zone = tables.objects.filter(restaurant__restaurant_name__contains=restaurant_name,place_of_table__pk__contains=x.pk)
        availabletimes.append(x.place_of_table)
        the_hours = hours_list[:]
        print('------------------this is the assign function---------------------')
        print('------------------zone---------------------')
        print(x)
        for y in tables_zone:
            print('------------------Current table---------------------')
            print(y)
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
                    print(save_necessary_people_one)
                    if save_necessary_people_one <= 0 and temporary_table == []:
                        ni = 0
                        while the_hours != []:
                            availabletimes.append(the_hours[ni])
                            the_hours.remove(the_hours[ni])
                        print('here -0')
                        return used_table_list
                        break
                    if save_necessary_people_one <= 0:
                        availabletimes.append(the_hours[ii])
                        the_hours.remove(the_hours[ii])
                        ii -= 1
                        print('here 0')
                        return used_table_list
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
                            used_table_list_one = used_table_list[:]
                            used_table_list_one.append(can_connect_list[ccl_two])
                            if save_necessary_people_two <= 0:
                                availabletimes.append(the_hours[ii])
                                the_hours.remove(the_hours[ii])
                                ii -= 1
                                print('here 1')
                                return used_table_list_one
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
                                    used_table_list_two = used_table_list_one[:]
                                    used_table_list_two.append(can_connect_list_two[ccl_three])
                                    if save_necessary_people_three <= 0:
                                        availabletimes.append(the_hours[ii])
                                        the_hours.remove(the_hours[ii])
                                        ii -= 1
                                        print('here 2')
                                        return used_table_list_two
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
                                            used_table_list_three = used_table_list_two[:]
                                            used_table_list_three.append(can_connect_list_three[ccl_four])
                                            if save_necessary_people_four <= 0:
                                                availabletimes.append(the_hours[ii])
                                                the_hours.remove(the_hours[ii])
                                                ii -= 1
                                                print('here 3')
                                                return used_table_list_three
                                                break
                                            can_connect_list_four = check_table[0].can_connect_tables[:]
                                            can_connect_list_four = can_connect_list_four.split(',')
                                            for utl in range(0, len(used_table_list_three), 1):
                                                for ccll in can_connect_list_four:
                                                    if ccll == used_table_list_three[utl]:
                                                        can_connect_list_four.remove(used_table_list_three[utl])
                                                        # not changed yet
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
                                                    used_table_list_four = used_table_list_three[:]
                                                    used_table_list_four.append(can_connect_list_four[ccl_five])
                                                    if save_necessary_people_five <= 0:
                                                        availabletimes.append(the_hours[ii])
                                                        the_hours.remove(the_hours[ii])
                                                        ii -= 1
                                                        print('here 4')
                                                        return used_table_list_four
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
                                                            used_table_list_five = used_table_list_four[:]
                                                            used_table_list_five.append(can_connect_list_five[ccl_six])
                                                            if save_necessary_people_six <= 0:
                                                                availabletimes.append(the_hours[ii])
                                                                the_hours.remove(the_hours[ii])
                                                                ii -= 1
                                                                print(used_table_list_three)
                                                                print(used_table_list_four)
                                                                print(used_table_list_five)
                                                                return used_table_list_five
                                                                break
                                                            can_connect_list_six = check_table[0].can_connect_tables[:]
                                                            can_connect_list_six = can_connect_list_six.split(',')
                                                            for utl in range(0, len(used_table_list_five), 1):
                                                                for ccll in can_connect_list_six:
                                                                    if ccll == used_table_list_five[utl]:
                                                                        can_connect_list_six.remove(used_table_list_five[utl])


    return 0
