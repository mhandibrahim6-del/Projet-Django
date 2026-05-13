import urllib.request
import urllib.parse
import base64
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import generics
from django.utils import timezone
from datetime import timedelta
from .models import DHT11, Seuil
from .serializers import DHT11Serializer

TWILIO_FROM = 'whatsapp:+14155238886'


@api_view(['GET'])
def liste_mesures(request):
    mesures = DHT11.objects.all().order_by('-date')
    serializer = DHT11Serializer(mesures, many=True)
    return Response(serializer.data)


@api_view(['GET'])
def derniere_mesure(request):
    mesure = DHT11.objects.order_by('-date').first()
    if mesure is None:
        return Response({"message": "Aucune donnée"})
    serializer = DHT11Serializer(mesure)
    return Response(serializer.data)


def _envoyer_whatsapp(sid, token, to, message):
    url  = f"https://api.twilio.com/2010-04-01/Accounts/{sid}/Messages.json"
    data = urllib.parse.urlencode({
        'From': TWILIO_FROM,
        'To'  : f'whatsapp:{to}',
        'Body': message,
    }).encode('utf-8')
    creds = base64.b64encode(f"{sid}:{token}".encode()).decode()
    req = urllib.request.Request(url, data=data, headers={
        'Authorization': f'Basic {creds}',
        'Content-Type' : 'application/x-www-form-urlencoded',
    })
    urllib.request.urlopen(req, timeout=10)


class AjouterMesure(generics.CreateAPIView):
    queryset = DHT11.objects.all()
    serializer_class = DHT11Serializer

    def perform_create(self, serializer):
        instance = serializer.save()
        seuil = Seuil.objects.first()
        if not seuil or not seuil.twilio_sid or not seuil.whatsapp_to:
            return

        maintenant = timezone.now()
        cooldown   = timedelta(minutes=5)

        if instance.temperature > seuil.temp_max:
            if not seuil.derniere_alerte_temp or (maintenant - seuil.derniere_alerte_temp) >= cooldown:
                try:
                    _envoyer_whatsapp(
                        seuil.twilio_sid, seuil.twilio_token, seuil.whatsapp_to,
                        f"ALERTE DHT11 - Temperature: {instance.temperature}C depasse le seuil de {seuil.temp_max}C"
                    )
                    seuil.derniere_alerte_temp = maintenant
                    seuil.save(update_fields=['derniere_alerte_temp'])
                except Exception:
                    pass

        if instance.humidite > seuil.humidite_max:
            if not seuil.derniere_alerte_humid or (maintenant - seuil.derniere_alerte_humid) >= cooldown:
                try:
                    _envoyer_whatsapp(
                        seuil.twilio_sid, seuil.twilio_token, seuil.whatsapp_to,
                        f"ALERTE DHT11 - Humidite: {instance.humidite}% depasse le seuil de {seuil.humidite_max}%"
                    )
                    seuil.derniere_alerte_humid = maintenant
                    seuil.save(update_fields=['derniere_alerte_humid'])
                except Exception:
                    pass