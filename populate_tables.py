import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from base.models import tables, placeOfTable
from base.models import restaurants

num_tables = 30  # Set the number of tables you want to create
num_seats = 3   # Set the number of seats for each table
place_of_table_name = 'outside'  # Set the ID of the placeOfTable you want to assign to the tables

# Fetch the restaurant and placeOfTable instances
restaurant_instance = restaurants.objects.get(pk__exact=1)
place_of_table_instance = placeOfTable.objects.get(place_of_table__contains=place_of_table_name)

for i in range(1, num_tables + 1):
    table_number = i
    number_of_seats = num_seats

    if i == 1:
        can_connect_tables = f"{i + 1}"
    elif i == num_tables:
        can_connect_tables = f"{i - 1}"
    else:
        can_connect_tables = f"{i - 1},{i + 1}"

    table = tables(
        restaurant=restaurant_instance,
        table_number=table_number,
        number_of_seats=number_of_seats,
        place_of_table=place_of_table_instance,
        can_connect_tables=can_connect_tables,
    )
    table.save()

print("Tables created successfully!")