from django.db import models
from django.contrib.auth import get_user_model
from datetime import datetime
User = get_user_model()

# Create your models here.
class restaurants(models.Model):
    owner = models.ForeignKey(User,related_name='restaurant_owner',on_delete=models.CASCADE)
    restaurant_name = models.CharField(max_length=254,unique=True)
    adress = models.CharField(max_length=254,unique=False)
    number_of_chairs = models.PositiveIntegerField()
    number_of_babychairs = models.PositiveIntegerField()
    restaurant_img = models.FileField(upload_to='restaurant_img')

    def __str__(self):
        return self.restaurant_name

class placeOfTable(models.Model):
    restaurant = models.ForeignKey(restaurants,related_name='restaurantplaceoftable',on_delete=models.CASCADE)
    place_of_table = models.CharField(max_length=254,unique=False)

    def __str__(self):
        return self.place_of_table


class tables(models.Model):
    restaurant = models.ForeignKey(restaurants,related_name='restauranttable',on_delete=models.CASCADE)
    table_number = models.CharField(max_length=254,unique=False)
    number_of_seats = models.CharField(max_length=254,unique=False)
    place_of_table = models.ForeignKey(placeOfTable,related_name='places',on_delete=models.CASCADE)
    can_connect_tables = models.CharField(max_length=254,unique=False)

    def __str__(self):
        return self.table_number

class restaurantOpenDaysOfTheWeek(models.Model):
    shifts = (
        ('Breakfast', 'Breakfast'),
        ('Lunch', 'Lunch'),
        ('Dinner', 'Dinner'),
    )

    restaurant = models.ForeignKey(restaurants,related_name='restaurantopentime',on_delete=models.CASCADE)
    Monday = models.BooleanField(default=0)
    Tuesday = models.BooleanField(default=0)
    Wednesday = models.BooleanField(default=0)
    Thursday = models.BooleanField(default=0)
    Friday = models.BooleanField(default=0)
    Saturday = models.BooleanField(default=0)
    Sunday = models.BooleanField(default=0)
    shift = models.CharField(max_length=254,choices=shifts)
    start_time = models.TimeField()
    end_time = models.TimeField()

    def __str__(self):
        return self.shift

class closedExceptions(models.Model):
    restaurant = models.ForeignKey(restaurants,related_name='restaurantclosedexceptions',on_delete=models.CASCADE)
    closed_days_start = models.DateField(default=datetime.now)
    closed_days_end = models.DateField(default=datetime.now)
    time_start = models.TimeField(default=datetime.now)
    time_end = models.TimeField(default=datetime.now)
    number_of_acceptance = models.CharField(max_length=254, default='')


    def __int__(self):
        return self.closed_days

class estimatedTimeCustomersSpend(models.Model):
    restaurant = models.ForeignKey(restaurants,related_name='restaurantestimatedtime',on_delete=models.CASCADE)
    number_of_people = models.PositiveIntegerField()
    estimated_time = models.TimeField()

    def __int__(self):
        return self.number_of_people

class limitOfCustomersPerHour(models.Model):
    restaurant = models.ForeignKey(restaurants,related_name='restaurantlimitcustomerperhour',on_delete=models.CASCADE)
    Monday = models.BooleanField(default=0)
    Tuesday = models.BooleanField(default=0)
    Wednesday = models.BooleanField(default=0)
    Thursday = models.BooleanField(default=0)
    Friday = models.BooleanField(default=0)
    Saturday = models.BooleanField(default=0)
    Sunday = models.BooleanField(default=0)
    number_of_people = models.PositiveIntegerField()
    start_time = models.TimeField()
    end_time = models.TimeField()


    def __int__(self):
        return self.start_time

class timeDivider(models.Model):
    minutes = (
        ('00:05', '00:05'),
        ('00:10', '00:10'),
        ('00:15', '00:15'),
        ('00:20', '00:20'),
        ('00:30', '00:30'),
        ('00:45', '00:45'),
        ('01:00', '01:00'),
        ('01:15', '01:15'),
        ('01:30', '01:30'),
        ('02:00', '02:00'),
    )
    restaurant = models.ForeignKey(restaurants,related_name='restauranttimedivider',on_delete=models.CASCADE)
    each_time = models.CharField(max_length=254,choices=minutes,default='00:15')

    def __char__(self):
        return self.number_of_tables

class numberOfPeopleWhenTablesConnect(models.Model):
    restaurant = models.ForeignKey(restaurants,related_name='restaurantnumberofpeopleperconnectedtable',on_delete=models.CASCADE)
    number_of_tables = models.PositiveIntegerField()
    number_of_chairs = models.IntegerField()

    def __int__(self):
        return self.number_of_tables
