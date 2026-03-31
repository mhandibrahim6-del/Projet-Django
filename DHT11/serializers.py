from rest_framework import serializers
from rest_framework import serializers
from .models import DHT11

class DHT11Serializer(serializers.ModelSerializer):
    class Meta:
        model = DHT11
        fields = ['temperature', 'humidite', 'date']