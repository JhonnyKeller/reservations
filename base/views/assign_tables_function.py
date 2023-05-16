from django.shortcuts import render
from base.models import (tables,placeOfTable,numberOfPeopleWhenTablesConnect)

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


def find_tables(the_hours,estimated_time,can_connect_list,used_table_list,save_necessary_people,connect_logic_number,tables_used,connect_logic, zone):
    print('(----------------- find tables start ----------------)')
    print('zone:', zone)
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
            if int(tables_used[i])  == int(can_connect_list[ccl]):
                temporary_table.append(tables_used[i])
                temporary_table.append(tables_used[i+1])
                temporary_table.append(tables_used[i+2])
        verify_hour = False
        if temporary_table != []:
            print('if temporary_table != []: It means there is reservations for the table being verified and it needs to be verified.')
            for tt in range(0,len(temporary_table),3):
                verify_hour = verify_hour_availability(the_hours,temporary_table[tt+1],temporary_table[tt+2],estimated_time)
                if verify_hour == False:
                    break
            if verify_hour:
                check_table = tables.objects.filter(table_number__contains=can_connect_list[ccl],place_of_table__place_of_table__contains=zone)
                save_necessary_people_two = save_necessary_people
                save_necessary_people_two -= int(check_table[0].number_of_seats) + connect_logic[connect_logic_number].number_of_chairs
                used_table_list_one = used_table_list[:]
                used_table_list_one.append(can_connect_list[ccl])
                if save_necessary_people_two <= 0:
                    return used_table_list_one
                else:
                    if connect_logic_number == 0:
                        connect_logic_number_save = connect_logic_number + 1
                    elif connect_logic_number == 2:
                        connect_logic_number_save = connect_logic_number - 1
                    else:
                        connect_logic_number_save = connect_logic_number + 1
                    can_connect_list_two = check_table[0].can_connect_tables[:]
                    can_connect_list_two = can_connect_list_two.split(',')
                    found_table = find_tables(the_hours,estimated_time,can_connect_list_two,used_table_list_one,save_necessary_people_two,connect_logic_number_save,tables_used,connect_logic, zone)
                    if found_table != 0:
                        return found_table
        if temporary_table == []:
            print('if temporary_table == []: It means there is no reservations for the table being verified and it does not need to be verified.')
            check_table = tables.objects.filter(table_number__contains=can_connect_list[ccl], place_of_table__place_of_table__contains=zone)
            save_necessary_people_two = save_necessary_people
            save_necessary_people_two -= int(check_table[0].number_of_seats) + connect_logic[connect_logic_number].number_of_chairs
            used_table_list_one = used_table_list[:]
            used_table_list_one.append(can_connect_list[ccl])
            if save_necessary_people_two <= 0:
                print('return 1')
                print('used_table_list_one', used_table_list_one)
                return used_table_list_one
            else:
                if connect_logic_number == 0:
                    connect_logic_number_save = connect_logic_number + 1
                elif connect_logic_number == 2:
                    connect_logic_number_save = connect_logic_number - 1
                else:
                    connect_logic_number_save = connect_logic_number + 1
                can_connect_list_two = check_table[0].can_connect_tables[:]
                can_connect_list_two = can_connect_list_two.split(',')
                found_table = find_tables(the_hours,estimated_time,can_connect_list_two,used_table_list_one,save_necessary_people_two,connect_logic_number_save,tables_used,connect_logic,zone)
                if found_table != 0:
                    print('return 2')
                    print('found_table', found_table)
                    return found_table
    return 0


def assignThTables(tables_used, necessary_people, estimated_time, restaurant_id, hours_list, zone):
    print('tables_used: ', tables_used)
    print('zone: ', zone)
    print('necessary_people: ', necessary_people)
    print('estimated_time (estimated time customer will spend): ', estimated_time)
    print('hours_list (time to make reservation): ', hours_list)
    print('restaurant_id: ', restaurant_id)
    connect_logic = numberOfPeopleWhenTablesConnect.objects.filter(restaurant__pk__exact=restaurant_id)
    zones = placeOfTable.objects.filter(restaurant__pk__exact=restaurant_id,place_of_table__contains=zone)
    availabletimes = []
    temporary_table = []
    for x in zones:
        tables_zone = tables.objects.filter(restaurant__pk__exact=restaurant_id,place_of_table__pk__contains=x.pk)
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
                used_table_list = []
                temporary_table = []
                for i in range(0, len(tables_used), 3):
                    if int(tables_used[i])  == int(y.table_number):
                        temporary_table.append(tables_used[i])
                        temporary_table.append(tables_used[i+1])
                        temporary_table.append(tables_used[i+2])
                verify_hour = True
                if temporary_table != []:
                    print('if temporary_table != []: It means there is reservations for the table being verified and it needs to be verified.')
                    for tt in range(0,len(temporary_table),3):
                        verify_hour = verify_hour_availability(the_hours[ii],temporary_table[tt+1],temporary_table[tt+2],estimated_time)
                        if verify_hour == False:
                            break
                    if verify_hour:
                        save_necessary_people_one = save_necessary_people
                        save_necessary_people_one -= int(y.number_of_seats)
                        used_table_list.append(y.table_number)
                        if save_necessary_people_one <= 0:
                            return used_table_list
                        can_connect_list = y.can_connect_tables[:]
                        can_connect_list = can_connect_list.split(',')
                        find_the_table = find_tables(the_hours[ii],estimated_time,can_connect_list,used_table_list,save_necessary_people_one,0,tables_used,connect_logic, zone)
                        if find_the_table != 0:
                            return find_the_table
                if temporary_table == []:
                    print('if temporary_table == []: It means there is no reservations for the table being verified and it does not need to be verified.')
                    save_necessary_people_one = save_necessary_people
                    save_necessary_people_one -= int(y.number_of_seats)
                    used_table_list.append(y.table_number)
                    if save_necessary_people_one <= 0:
                        return used_table_list
                    can_connect_list = y.can_connect_tables[:]
                    can_connect_list = can_connect_list.split(',')
                    find_the_table = find_tables(the_hours[ii],estimated_time,can_connect_list,used_table_list,save_necessary_people_one,0,tables_used,connect_logic, zone)
                    print('find_the_table: ', find_the_table)
                    if find_the_table != 0:   # if it's different then zero return the found tables
                        return find_the_table
    return []