# Generated by Django 4.1.3 on 2022-12-16 17:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('restaurants', '0011_remove_limitofcustomersperhour_each_time_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='limitofcustomersperhour',
            name='weekdays',
        ),
        migrations.AddField(
            model_name='limitofcustomersperhour',
            name='Friday',
            field=models.BooleanField(default=0),
        ),
        migrations.AddField(
            model_name='limitofcustomersperhour',
            name='Monday',
            field=models.BooleanField(default=0),
        ),
        migrations.AddField(
            model_name='limitofcustomersperhour',
            name='Saturday',
            field=models.BooleanField(default=0),
        ),
        migrations.AddField(
            model_name='limitofcustomersperhour',
            name='Sunday',
            field=models.BooleanField(default=0),
        ),
        migrations.AddField(
            model_name='limitofcustomersperhour',
            name='Thursday',
            field=models.BooleanField(default=0),
        ),
        migrations.AddField(
            model_name='limitofcustomersperhour',
            name='Tuesday',
            field=models.BooleanField(default=0),
        ),
        migrations.AddField(
            model_name='limitofcustomersperhour',
            name='Wednesday',
            field=models.BooleanField(default=0),
        ),
        migrations.AlterField(
            model_name='timedivider',
            name='each_time',
            field=models.CharField(choices=[('00:05', '00:05'), ('00:10', '00:10'), ('00:15', '00:15'), ('00:20', '00:20'), ('00:30', '00:30'), ('00:45', '00:45'), ('01:00', '01:00'), ('01:15', '01:15'), ('01:30', '01:30'), ('02:00', '02:00')], default='00:15', max_length=254),
        ),
    ]
