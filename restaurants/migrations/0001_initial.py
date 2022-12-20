# Generated by Django 4.1.3 on 2022-12-06 15:38

import datetime
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='placeOfTable',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('place_of_table', models.CharField(max_length=254, unique=True)),
            ],
        ),
        migrations.CreateModel(
            name='restaurants',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('restaurant_name', models.CharField(max_length=254, unique=True)),
                ('adress', models.CharField(max_length=254, unique=True)),
                ('number_of_chairs', models.PositiveIntegerField()),
                ('number_of_babychairs', models.PositiveIntegerField()),
                ('restaurant_img', models.FileField(upload_to='restaurant_img')),
                ('owner', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='restaurant_owner', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='tables',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('table_number', models.CharField(max_length=254, unique=True)),
                ('number_of_seats', models.CharField(max_length=254, unique=True)),
                ('can_connect_tables', models.CharField(max_length=254, unique=True)),
                ('place_of_table', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='places', to='restaurants.placeoftable')),
                ('restaurant', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='restauranttable', to='restaurants.restaurants')),
            ],
        ),
        migrations.CreateModel(
            name='restaurantOpenDaysOfTheWeek',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('weekday', models.CharField(choices=[('Monday', 'Monday'), ('Tuesday', 'Tuesday'), ('Wenesday', 'Wenesday'), ('Thursday', 'Thursday'), ('Friday', 'Friday'), ('Saturday', 'Saturday'), ('Sunday', 'Sunday')], max_length=254)),
                ('shift', models.CharField(choices=[('Breakfast', 'Breakfast'), ('Lunch', 'Lunch'), ('Dinner', 'Dinner')], max_length=254)),
                ('start_time', models.TimeField()),
                ('end_time', models.TimeField()),
                ('restaurant', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='restaurantopentime', to='restaurants.restaurants')),
            ],
        ),
        migrations.AddField(
            model_name='placeoftable',
            name='restaurant',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='restaurantplaceoftable', to='restaurants.restaurants'),
        ),
        migrations.CreateModel(
            name='numberOfPeopleWhenTablesConnect',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('number_of_tables', models.PositiveIntegerField()),
                ('number_of_chairs', models.PositiveIntegerField()),
                ('restaurant', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='restaurantnumberofpeopleperconnectedtable', to='restaurants.restaurants')),
            ],
        ),
        migrations.CreateModel(
            name='estimatedTimeTillCustomerLeaves',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('number_of_people', models.PositiveIntegerField()),
                ('time', models.TimeField(default=datetime.datetime.now)),
                ('restaurant', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='restaurantshiftcustomer', to='restaurants.restaurants')),
            ],
        ),
        migrations.CreateModel(
            name='estimatedTimeCustomersSpend',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('number_of_people', models.PositiveIntegerField()),
                ('estimated_time', models.TimeField()),
                ('restaurant', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='restaurantestimatedtime', to='restaurants.restaurants')),
            ],
        ),
        migrations.CreateModel(
            name='closedExceptions',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('closed_days', models.DateField()),
                ('restaurant', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='restaurantclosedexceptions', to='restaurants.restaurants')),
            ],
        ),
    ]
