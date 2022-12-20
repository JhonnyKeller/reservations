from django import forms
from django.forms import ModelForm
from .models import reservations
from captcha.fields import ReCaptchaField

class  reservationsForm(ModelForm):
    captcha = ReCaptchaField()
    class Meta:
        model = reservations
        exclude = ['tablesused','time','estimatedtime','restaurant','table_place_preference','date']
