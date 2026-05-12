from django.shortcuts import render
from django.utils.dateparse import parse_datetime
from .models import DHT11

def dashboard(request):
    mesure = DHT11.objects.order_by('-date').first()

    date_debut = request.GET.get('date_debut')
    date_fin   = request.GET.get('date_fin')

    mesures = DHT11.objects.order_by('-date')

    if date_debut:
        mesures = mesures.filter(date__gte=parse_datetime(date_debut))
    if date_fin:
        mesures = mesures.filter(date__lte=parse_datetime(date_fin))

    if not date_debut and not date_fin:
        mesures = mesures[:100]

    return render(request, 'dashboard.html', {
        'mesure': mesure,
        'mesures': mesures,
        'date_debut': date_debut or '',
        'date_fin':   date_fin or '',
    })
