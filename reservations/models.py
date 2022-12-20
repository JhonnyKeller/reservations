from django.db import models
from phonenumber_field.modelfields import PhoneNumberField
from restaurants.models import placeOfTable,restaurants,restaurantOpenDaysOfTheWeek

# Create your models here.
class reservations(models.Model):
    shifts = (
        ('Breakfast', 'Breakfast'),
        ('Lunch', 'Lunch'),
        ('Dinner', 'Dinner'),
    )
    restaurant = models.ForeignKey(restaurants,related_name='restaurant_of_reservation',on_delete=models.CASCADE)
    full_name = models.CharField(max_length=254)
    email = models.EmailField(max_length=254)
    phone_number = PhoneNumberField()
    date = models.DateField()
    shift = models.CharField(max_length=254,choices=shifts,default=shifts[0][0])
    time = models.CharField(max_length=254)
    estimatedtime = models.CharField(max_length=254,default='')
    tablesused = models.CharField(max_length=254,default='')
    table_place_preference = models.ForeignKey(placeOfTable,related_name='placeoftable',on_delete=models.CASCADE)
    number_of_people = models.PositiveIntegerField()
    baby_chair = models.PositiveIntegerField()
    message = models.CharField(max_length=254)

    def __str__(self):
        return self.full_name
