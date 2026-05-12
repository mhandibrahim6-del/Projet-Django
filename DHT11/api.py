from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import generics
from urllib.request import urlopen
from urllib.parse import quote
from .models import DHT11, Seuil
from .serializers import DHT11Serializer


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


def _envoyer_whatsapp(telephone, apikey, message):
    url = (
        "https://api.callmebot.com/whatsapp.php"
        f"?phone={telephone}&text={quote(message)}&apikey={apikey}"
    )
    try:
        urlopen(url, timeout=10)
    except Exception:
        pass


class AjouterMesure(generics.CreateAPIView):
    queryset = DHT11.objects.all()
    serializer_class = DHT11Serializer

    def perform_create(self, serializer):
        instance = serializer.save()
        seuil = Seuil.objects.first()
        if not seuil or not seuil.telephone or not seuil.apikey:
            return
        if instance.temperature > seuil.temp_max:
            _envoyer_whatsapp(
                seuil.telephone, seuil.apikey,
                f"ALERTE Temperature: {instance.temperature}°C depasse le seuil de {seuil.temp_max}°C"
            )
        if instance.humidite > seuil.humidite_max:
            _envoyer_whatsapp(
                seuil.telephone, seuil.apikey,
                f"ALERTE Humidite: {instance.humidite}% depasse le seuil de {seuil.humidite_max}%"
            )