from django import forms
from django.forms import ModelForm
from .models import (restaurants,placeOfTable,tables,restaurantOpenDaysOfTheWeek,
                    closedExceptions,estimatedTimeCustomersSpend,
                    numberOfPeopleWhenTablesConnect,limitOfCustomersPerHour,
                    timeDivider)

class  restaurantsForm(ModelForm):
    class Meta:
        model = restaurants
        fields = '__all__'

class  restaurantsOpenDaysForm(ModelForm):
    class Meta:
        model = restaurantOpenDaysOfTheWeek
        fields = '__all__'

class  restaurantsClosedDaysForm(ModelForm):
    class Meta:
        model = closedExceptions
        fields = '__all__'

class  restaurantsEstimatedTimeForm(ModelForm):
    class Meta:
        model = estimatedTimeCustomersSpend
        fields = '__all__'

class  placeOfTableForm(ModelForm):
    class Meta:
        model = placeOfTable
        fields = '__all__'

class  tablesForm(ModelForm):
    class Meta:
        model = tables
        fields = '__all__'

class  numberOfPeopleWhenTablesConnectForm(ModelForm):
    class Meta:
        model = numberOfPeopleWhenTablesConnect
        fields = '__all__'

class  limitOfCustomersPerHourForm(ModelForm):
    class Meta:
        model = limitOfCustomersPerHour
        fields = '__all__'

class  timeDividerForm(ModelForm):
    class Meta:
        model = timeDivider
        fields = '__all__'
