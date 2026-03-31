from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import generics
from .models import DHT11
from .serializers import DHT11Serializer

# =========================
# GET : toutes les mesures
# =========================
@api_view(['GET'])
def liste_mesures(request):
    mesures = DHT11.objects.all().order_by('-date')
    serializer = DHT11Serializer(mesures, many=True)
    return Response(serializer.data)


# =========================
# GET : dernière mesure
# =========================
@api_view(['GET'])
def derniere_mesure(request):
    mesure = DHT11.objects.order_by('-date').first()
    if mesure is None:
        return Response({"message": "Aucune donnée"})
    serializer = DHT11Serializer(mesure)
    return Response(serializer.data)


# =========================
# POST : ajouter mesure
# =========================
class AjouterMesure(generics.CreateAPIView):
    queryset = DHT11.objects.all()
    serializer_class = DHT11Serializer