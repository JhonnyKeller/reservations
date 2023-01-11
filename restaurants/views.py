from django.shortcuts import render
from .models import (restaurants,placeOfTable,tables,restaurantOpenDaysOfTheWeek,
                    closedExceptions,estimatedTimeCustomersSpend,
                    numberOfPeopleWhenTablesConnect,limitOfCustomersPerHour,timeDivider)
from .forms import (restaurantsForm,restaurantsOpenDaysForm,restaurantsClosedDaysForm,
                    restaurantsEstimatedTimeForm,placeOfTableForm,tablesForm,
                    numberOfPeopleWhenTablesConnectForm,limitOfCustomersPerHourForm,timeDividerForm)
from datetime import timedelta, date, datetime
from reservations.models import reservations
from reservations.views import numbers_to_weekday




# Utility functions ------------------------------------------------------------




# views ------------------------------------------------------------------------
def createrestaurant(request):
    restaurant = restaurants.objects.filter(owner__username__contains=request.user)
    restaurant_form = restaurantsForm()
    name = request.POST.get('restaurant_name', '')
    if_create_true = 'False'
    print(name)

    if request.method == 'POST':
        if_create_true = request.POST.get('if_create_true', 'False')
        form = restaurantsForm(request.POST,request.FILES)
        if form.is_valid():
            save = form.save(commit=False)
            save.save()
            instance = restaurants.objects.get(restaurant_name=name)
            y = 5
            for x in range(2,y,1):
                connect_tables_form = numberOfPeopleWhenTablesConnect(restaurant=instance,number_of_tables=x,number_of_chairs=-2)
                connect_tables_form.save()
            divider_form = timeDivider(restaurant=instance)
            divider_form.save()
            if_create_true = 'False'




    return render(request,'restaurants/createrestaurant.html', {'restaurant':restaurant,'restaurant_form':restaurant_form,
                                                                'if_create_true':if_create_true,})


def restaurantmenu(request, restaurant_pk):
    zones = placeOfTable.objects.filter(restaurant__pk__exact=restaurant_pk)
    today = date.today()
    date_true = 'False'
    choosenday = today.strftime("%Y-%m-%d")
    owner_restaurants = restaurants.objects.filter(owner__username__contains=request.user)
    restaurant = restaurants.objects.filter(owner__username__contains=request.user,pk__exact=restaurant_pk)
    reservation_breakfast = reservations.objects.filter(restaurant__pk__exact=restaurant_pk,
                                                        date__contains=choosenday,
                                                        shift__contains='Breakfast')
    reservation_lunch = reservations.objects.filter(restaurant__pk__exact=restaurant_pk,
                                                    date__contains=choosenday,
                                                    shift__contains='Lunch')
    reservation_dinner = reservations.objects.filter(restaurant__pk__exact=restaurant_pk,
                                                     date__contains=choosenday,
                                                     shift__contains='Dinner')
    choosenday = datetime.strptime(choosenday,"%Y-%m-%d")
    choosenday = choosenday.strftime("%m/%d/%Y")
    if request.method == 'POST':
        choosenday = request.POST.get('choosenday',today.strftime("%Y-%m-%d"))
        choosenday = datetime.strptime(choosenday,"%m/%d/%Y")
        reservation_breakfast = reservations.objects.filter(restaurant__pk__contains=restaurant_pk,
                                                            date__contains=choosenday.strftime("%Y-%m-%d"),
                                                            shift__contains='Breakfast')
        reservation_lunch = reservations.objects.filter(restaurant__pk__contains=restaurant_pk,
                                                        date__contains=choosenday.strftime("%Y-%m-%d"),
                                                        shift__contains='Lunch')
        reservation_dinner = reservations.objects.filter(restaurant__pk__contains=restaurant_pk,
                                                         date__contains=choosenday.strftime("%Y-%m-%d"),
                                                         shift__contains='Dinner')
        choosenday = choosenday.strftime("%m/%d/%Y")

    return render(request, 'restaurants/restaurantmenu.html',{'restaurant':restaurant,
                                                              'owner_restaurants':owner_restaurants,
                                                              'reservation_breakfast':reservation_breakfast,
                                                              'reservation_lunch':reservation_lunch,
                                                              'reservation_dinner':reservation_dinner,
                                                              'choosenday':choosenday,'zones':zones})

def createZones(request, restaurant_pk):
    form_to_update = ''
    form_update = ''
    delete = request.POST.get('delete','False')
    delete_confirm = request.POST.get('delete_confirm','False')
    create_form = request.POST.get('create_form','False')
    save_form = request.POST.get('save_form','False')
    form_pk = request.POST.get('form_pk','False')
    save_form_update = request.POST.get('save_form_update','False')
    restaurant = restaurants.objects.filter(owner__username__contains=request.user,pk__exact=restaurant_pk)
    owner_restaurants = restaurants.objects.filter(owner__username__contains=request.user)
    data = placeOfTable.objects.filter(restaurant__pk__exact=restaurant_pk)
    form = placeOfTableForm()

    if request.method == 'POST':
        if save_form == 'True':
            form = placeOfTableForm(request.POST)
            if form.is_valid():
                save = form.save(commit=False)
                save.save()
        if form_pk != 'False':
            form_to_update = placeOfTable.objects.get(pk__exact=form_pk)
            form_update = placeOfTableForm(instance=form_to_update)
            if save_form_update == 'True':
                form_update = placeOfTableForm(request.POST,instance=form_to_update)
                if form_update.is_valid():
                    form_update.save()
                    form_pk = 'False'
        if delete != 'False':
            print(delete)
            instance = placeOfTable.objects.get(pk=delete)
            if delete_confirm == 'True':
                instance.delete()
                delete = 'False'
    return render(request, 'restaurants/create_zones.html', {'restaurant':restaurant,
                                                             'owner_restaurants':owner_restaurants,
                                                             'form':form,'data':data,
                                                             'create_form':create_form,
                                                             'form_pk':form_pk,'form_update':form_update,
                                                             'delete':delete})

def createTables(request, restaurant_pk):
    zones = placeOfTable.objects.filter(restaurant__owner__username__contains=request.user,restaurant__pk__exact=restaurant_pk)
    form_to_update = ''
    form_update = ''
    delete = request.POST.get('delete','False')
    delete_confirm = request.POST.get('delete_confirm','False')
    create_form = request.POST.get('create_form','False')
    save_form = request.POST.get('save_form','False')
    form_pk = request.POST.get('form_pk','False')
    save_form_update = request.POST.get('save_form_update','False')
    restaurant = restaurants.objects.filter(owner__username__contains=request.user,pk__exact=restaurant_pk)
    owner_restaurants = restaurants.objects.filter(owner__username__contains=request.user)
    data = tables.objects.filter(restaurant__pk__exact=restaurant_pk)
    form = tablesForm()

    if request.method == 'POST':
        if save_form == 'True':
            form = tablesForm(request.POST)
            if form.is_valid():
                save = form.save(commit=False)
                save.save()
        if form_pk != 'False':
            form_to_update = tables.objects.get(pk=form_pk)
            form_update = tablesForm(instance=form_to_update)
            if save_form_update == 'True':
                form_update = tablesForm(request.POST,instance=form_to_update)
                if form_update.is_valid():
                    form_update.save()
                    form_pk = 'False'
        if delete != 'False':
            print(delete)
            instance = tables.objects.get(pk=delete)
            if delete_confirm == 'True':
                instance.delete()
                delete = 'False'
    return render(request, 'restaurants/create_tables.html', {'restaurant':restaurant,
                                                              'owner_restaurants':owner_restaurants,
                                                              'form':form,'data':data,
                                                              'create_form':create_form,
                                                              'form_pk':form_pk,'form_update':form_update,
                                                              'delete':delete,'zones':zones})

def connectTables(request, restaurant_pk):
    form_to_update = ''
    form_update = ''
    delete = request.POST.get('delete','False')
    delete_confirm = request.POST.get('delete_confirm','False')
    create_form = request.POST.get('create_form','False')
    save_form = request.POST.get('save_form','False')
    form_pk = request.POST.get('form_pk','False')
    save_form_update = request.POST.get('save_form_update','False')
    restaurant = restaurants.objects.filter(owner__username__contains=request.user,pk__exact=restaurant_pk)
    owner_restaurants = restaurants.objects.filter(owner__username__contains=request.user)
    data = numberOfPeopleWhenTablesConnect.objects.filter(restaurant__pk__exact=restaurant_pk)
    form = numberOfPeopleWhenTablesConnectForm()

    if request.method == 'POST':
        if save_form == 'True':
            form = numberOfPeopleWhenTablesConnectForm(request.POST)
            if form.is_valid():
                save = form.save(commit=False)
                save.save()
        if form_pk != 'False':
            form_to_update = numberOfPeopleWhenTablesConnect.objects.get(pk__exact=form_pk)
            form_update = numberOfPeopleWhenTablesConnectForm(instance=form_to_update)
            if save_form_update == 'True':
                form_update = numberOfPeopleWhenTablesConnectForm(request.POST,instance=form_to_update)
                if form_update.is_valid():
                    form_update.save()
                    form_pk = 'False'
        if delete != 'False':
            print(delete)
            instance = numberOfPeopleWhenTablesConnect.objects.get(pk__exact=delete)
            if delete_confirm == 'True':
                instance.delete()
                delete = 'False'
    return render(request, 'restaurants/connect_tables.html', {'restaurant':restaurant,
                                                              'owner_restaurants':owner_restaurants,
                                                              'form':form,'data':data,
                                                              'create_form':create_form,
                                                              'form_pk':form_pk,'form_update':form_update,
                                                              'delete':delete})

def openDays(request, restaurant_pk):
    openDayToUpdate = ''
    form_update = ''
    delete = request.POST.get('delete','False')
    delete_confirm = request.POST.get('delete_confirm','False')
    create_openDay = request.POST.get('create_openDay','False')
    save_openDay = request.POST.get('save_openDay','False')
    openDayPK = request.POST.get('openDayPK','False')
    save_form_update = request.POST.get('save_form_update','False')
    restaurant = restaurants.objects.filter(owner__username__contains=request.user,pk__exact=restaurant_pk)
    owner_restaurants = restaurants.objects.filter(owner__username__contains=request.user)
    openDays = restaurantOpenDaysOfTheWeek.objects.filter(restaurant__pk__exact=restaurant_pk)
    form = restaurantsOpenDaysForm()

    if request.method == 'POST':
        if save_openDay == 'True':
            form = restaurantsOpenDaysForm(request.POST)
            if form.is_valid():
                save = form.save(commit=False)
                save.save()
        if openDayPK != 'False':
            openDayToUpdate = restaurantOpenDaysOfTheWeek.objects.get(pk__exact=openDayPK)
            print(openDayToUpdate)
            form_update = restaurantsOpenDaysForm(instance=openDayToUpdate)
            if save_form_update == 'True':
                form_update = restaurantsOpenDaysForm(request.POST,instance=openDayToUpdate)
                if form_update.is_valid():
                    form_update.save()
                    openDayPK = 'False'
        if delete != 'False':
            instance = restaurantOpenDaysOfTheWeek.objects.get(pk__exact=delete)
            if delete_confirm == 'True':
                instance.delete()
                delete = 'False'


    return render(request, 'restaurants/create_openDays.html', {'restaurant':restaurant,
                                                                'owner_restaurants':owner_restaurants,
                                                                'form':form,'openDays':openDays,
                                                                'create_openDay':create_openDay,
                                                                'openDayPK':openDayPK,'form_update':form_update,
                                                                'delete':delete})
def closedDays(request, restaurant_pk):
    form_to_update = ''
    form_update = ''
    delete = request.POST.get('delete','False')
    delete_confirm = request.POST.get('delete_confirm','False')
    create_form = request.POST.get('create_form','False')
    save_form = request.POST.get('save_form','False')
    form_pk = request.POST.get('form_pk','False')
    save_form_update = request.POST.get('save_form_update','False')
    restaurant = restaurants.objects.filter(owner__username__contains=request.user,pk__exact=restaurant_pk)
    owner_restaurants = restaurants.objects.filter(owner__username__contains=request.user)
    data = closedExceptions.objects.filter(restaurant__pk__exact=restaurant_pk)
    form = restaurantsClosedDaysForm()

    if request.method == 'POST':
        if save_form == 'True':
            form = restaurantsClosedDaysForm(request.POST)
            if form.is_valid():
                save = form.save(commit=False)
                save.save()
        if form_pk != 'False':
            form_to_update = closedExceptions.objects.get(pk=form_pk)
            form_update = restaurantsClosedDaysForm(instance=form_to_update)
            if save_form_update == 'True':
                form_update = restaurantsClosedDaysForm(request.POST,instance=form_to_update)
                if form_update.is_valid():
                    form_update.save()
                    form_pk = 'False'
        if delete != 'False':
            print(delete)
            instance = closedExceptions.objects.get(pk=delete)
            if delete_confirm == 'True':
                instance.delete()
                delete = 'False'
    return render(request, 'restaurants/create_closedDays.html', {'restaurant':restaurant,
                                                                'owner_restaurants':owner_restaurants,
                                                                'form':form,'data':data,
                                                                'create_form':create_form,
                                                                'form_pk':form_pk,'form_update':form_update,
                                                                'delete':delete})

def estimatedTime(request, restaurant_pk):
    form_to_update = ''
    form_update = ''
    delete = request.POST.get('delete','False')
    delete_confirm = request.POST.get('delete_confirm','False')
    create_form = request.POST.get('create_form','False')
    save_form = request.POST.get('save_form','False')
    form_pk = request.POST.get('form_pk','False')
    save_form_update = request.POST.get('save_form_update','False')
    restaurant = restaurants.objects.filter(owner__username__contains=request.user,pk__exact=restaurant_pk)
    owner_restaurants = restaurants.objects.filter(owner__username__contains=request.user)
    data = estimatedTimeCustomersSpend.objects.filter(restaurant__pk__exact=restaurant_pk)
    form = restaurantsEstimatedTimeForm()

    if request.method == 'POST':
        if save_form == 'True':
            form = restaurantsEstimatedTimeForm(request.POST)
            if form.is_valid():
                save = form.save(commit=False)
                save.save()
        if form_pk != 'False':
            form_to_update = estimatedTimeCustomersSpend.objects.get(pk=form_pk)
            form_update = restaurantsEstimatedTimeForm(instance=form_to_update)
            if save_form_update == 'True':
                form_update = restaurantsEstimatedTimeForm(request.POST,instance=form_to_update)
                if form_update.is_valid():
                    form_update.save()
                    form_pk = 'False'
        if delete != 'False':
            print(delete)
            instance = estimatedTimeCustomersSpend.objects.get(pk=delete)
            if delete_confirm == 'True':
                instance.delete()
                delete = 'False'
    return render(request, 'restaurants/estimated_time.html', {'restaurant':restaurant,
                                                                'owner_restaurants':owner_restaurants,
                                                                'form':form,'data':data,
                                                                'create_form':create_form,
                                                                'form_pk':form_pk,'form_update':form_update,
                                                                'delete':delete})

def limitOfCustomersPerHours(request, restaurant_pk):
    form_to_update = ''
    form_update = ''
    delete = request.POST.get('delete','False')
    delete_confirm = request.POST.get('delete_confirm','False')
    create_form = request.POST.get('create_form','False')
    save_form = request.POST.get('save_form','False')
    form_pk = request.POST.get('form_pk','False')
    save_form_update = request.POST.get('save_form_update','False')
    restaurant = restaurants.objects.filter(owner__username__contains=request.user,pk__exact=restaurant_pk)
    owner_restaurants = restaurants.objects.filter(owner__username__contains=request.user)
    data = limitOfCustomersPerHour.objects.filter(restaurant__pk__exact=restaurant_pk)
    form = limitOfCustomersPerHourForm()

    if request.method == 'POST':
        if save_form == 'True':
            form = limitOfCustomersPerHourForm(request.POST)
            if form.is_valid():
                save = form.save(commit=False)
                save.save()
        if form_pk != 'False':
            form_to_update = limitOfCustomersPerHour.objects.get(pk=form_pk)
            form_update = limitOfCustomersPerHourForm(instance=form_to_update)
            if save_form_update == 'True':
                form_update = limitOfCustomersPerHourForm(request.POST,instance=form_to_update)
                if form_update.is_valid():
                    form_update.save()
                    form_pk = 'False'
        if delete != 'False':
            print(delete)
            instance = limitOfCustomersPerHour.objects.get(pk=delete)
            if delete_confirm == 'True':
                instance.delete()
                delete = 'False'
    return render(request, 'restaurants/limit_customers_per_hour.html', {'restaurant':restaurant,
                                                                'owner_restaurants':owner_restaurants,
                                                                'form':form,'data':data,
                                                                'create_form':create_form,
                                                                'form_pk':form_pk,'form_update':form_update,
                                                                'delete':delete})

def restaurantSettings(request,restaurant_pk):
    form_pk = 'False'
    restaurant = restaurants.objects.filter(owner__username__contains=request.user,pk__exact=restaurant_pk)
    form_to_update = restaurants.objects.get(pk=restaurant_pk)
    form_to_update_time_divider = timeDivider.objects.get(restaurant__pk=restaurant_pk)
    form_update_time_divider = timeDividerForm(instance=form_to_update_time_divider)
    form_update = restaurantsForm(instance=form_to_update)
    owner_restaurants = restaurants.objects.filter(owner__username__contains=request.user)

    if request.method == 'POST':
        form_update = restaurantsForm(request.POST,instance=form_to_update)
        form_update_time_divider = timeDividerForm(request.POST,instance=form_to_update)
        if form_update.is_valid() and form_update_time_divider.is_valid():
            form_update.save()
            form_update_time_divider.save()
            form_pk = 'True'




    return render(request, 'restaurants/restaurant_settings.html', {'restaurant':restaurant,
                                                                         'owner_restaurants':owner_restaurants,
                                                                         'form_update':form_update,
                                                                         'form_pk':form_pk,
                                                                         'form_update_time_divider':form_update_time_divider,})
