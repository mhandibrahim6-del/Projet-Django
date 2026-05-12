from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.utils import timezone
from datetime import timedelta
from .models import DHT11, Seuil

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

    seuil = Seuil.objects.first()

    return render(request, 'dashboard.html', {
        'mesure'  : mesure,
        'mesures' : mesures,
        'periode' : periode,
        'debut'   : debut,
        'fin'     : fin,
        'seuil'   : seuil,
    })


def sauvegarder_seuil(request):
    if request.method == 'POST':
        seuil, _ = Seuil.objects.get_or_create(id=1)
        seuil.temp_max     = float(request.POST.get('temp_max', 30))
        seuil.humidite_max = float(request.POST.get('humidite_max', 80))
        seuil.topic        = request.POST.get('topic', '').strip()
        seuil.save()
    return redirect('/')


def tester_notification(request):
    seuil = Seuil.objects.first()
    if not seuil or not seuil.topic:
        return JsonResponse({'ok': False, 'erreur': 'Aucun topic configuré'})
    import urllib.request
    req = urllib.request.Request(
        f"https://ntfy.sh/{seuil.topic}",
        data="Test notification DHT11 - La connexion fonctionne !".encode('utf-8'),
        headers={'Title': 'Test DHT11', 'Priority': 'default', 'Tags': 'white_check_mark'},
        method='POST'
    )
    try:
        urllib.request.urlopen(req, timeout=10)
        return JsonResponse({'ok': True})
    except Exception as e:
        return JsonResponse({'ok': False, 'erreur': str(e)})
