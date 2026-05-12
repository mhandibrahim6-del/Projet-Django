from django.db import models

class DHT11(models.Model):
    temperature = models.FloatField()
    humidite = models.FloatField()
    date = models.DateTimeField(auto_now_add=True)

class Seuil(models.Model):
    temp_max              = models.FloatField(default=30.0)
    humidite_max          = models.FloatField(default=80.0)
    topic                 = models.CharField(max_length=100, default='')
    derniere_alerte_temp  = models.DateTimeField(null=True, blank=True)
    derniere_alerte_humid = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name = "Seuil d'alerte"