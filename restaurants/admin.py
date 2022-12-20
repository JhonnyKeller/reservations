from django.contrib import admin
from .models import (restaurants,placeOfTable,tables,restaurantOpenDaysOfTheWeek,
                     closedExceptions,estimatedTimeCustomersSpend,
                     numberOfPeopleWhenTablesConnect,limitOfCustomersPerHour,
                     timeDivider)

# Register your models here.
admin.site.register(restaurants)
admin.site.register(placeOfTable)
admin.site.register(tables)
admin.site.register(restaurantOpenDaysOfTheWeek)
admin.site.register(closedExceptions)
admin.site.register(estimatedTimeCustomersSpend)
admin.site.register(numberOfPeopleWhenTablesConnect)
admin.site.register(limitOfCustomersPerHour)
admin.site.register(timeDivider)
