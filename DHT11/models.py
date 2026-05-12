from django.db import models

class DHT11(models.Model):
    temperature = models.FloatField()
    humidite = models.FloatField()
    date = models.DateTimeField(auto_now_add=True)

class Seuil(models.Model):
    temp_max     = models.FloatField(default=30.0)
    humidite_max = models.FloatField(default=80.0)
    telephone    = models.CharField(max_length=20, default='')
    apikey       = models.CharField(max_length=50, default='')

    class Meta:
        verbose_name = "Seuil d'alerte"