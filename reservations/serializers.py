from rest_framework import serializers
from .models import reservations

class reservationsSerializer(serializers.ModelSerializer):
    class Meta:
        model = reservations
        fields = '__all__'
