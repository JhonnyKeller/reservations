# Generated by Django 4.1.3 on 2022-12-06 16:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('restaurants', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='tables',
            name='can_connect_tables',
            field=models.CharField(max_length=254),
        ),
        migrations.AlterField(
            model_name='tables',
            name='number_of_seats',
            field=models.CharField(max_length=254),
        ),
    ]