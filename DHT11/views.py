from django.shortcuts import render
from django.utils import timezone
from datetime import timedelta
from .models import DHT11

def dashboard(request):
    mesure = DHT11.objects.order_by('-date').first()

    periode = request.GET.get('periode', '24h')
    debut   = request.GET.get('debut', '')
    fin     = request.GET.get('fin', '')

    mesures = DHT11.objects.order_by('date')

    if debut and fin:
        mesures = mesures.filter(date__gte=debut, date__lte=fin)
        periode = 'custom'
    else:
        durees = {'1h': 1, '6h': 6, '24h': 24, '7j': 168, '30j': 720}
        heures = durees.get(periode, 24)
        since  = timezone.now() - timedelta(hours=heures)
        mesures = mesures.filter(date__gte=since)

    return render(request, 'dashboard.html', {
        'mesure'  : mesure,
        'mesures' : mesures,
        'periode' : periode,
        'debut'   : debut,
        'fin'     : fin,
    })
