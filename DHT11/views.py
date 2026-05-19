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


def page_config(request):
    seuil = Seuil.objects.first()
    return render(request, 'config.html', {'seuil': seuil})


def sauvegarder_seuil(request):
    if request.method == 'POST':
        seuil, _ = Seuil.objects.get_or_create(id=1)
        seuil.temp_max     = float(request.POST.get('temp_max', 30))
        seuil.humidite_max = float(request.POST.get('humidite_max', 80))
        seuil.twilio_sid   = request.POST.get('twilio_sid', '').strip()
        seuil.twilio_token = request.POST.get('twilio_token', '').strip()
        seuil.whatsapp_to  = request.POST.get('whatsapp_to', '').strip()
        seuil.save()
    return redirect('/')


def simuler_alerte(request):
    import urllib.request, urllib.parse, base64
    seuil  = Seuil.objects.first()
    mesure = DHT11.objects.order_by('-date').first()
    if not seuil or not seuil.twilio_sid or not seuil.whatsapp_to:
        return JsonResponse({'ok': False, 'erreur': 'WhatsApp non configuré'})
    if not mesure:
        return JsonResponse({'ok': False, 'erreur': 'Aucune mesure en base'})
    alertes = []
    if mesure.temperature > seuil.temp_max:
        alertes.append(f"Temperature: {mesure.temperature}C depasse le seuil de {seuil.temp_max}C")
    if mesure.humidite > seuil.humidite_max:
        alertes.append(f"Humidite: {mesure.humidite}% depasse le seuil de {seuil.humidite_max}%")
    if not alertes:
        return JsonResponse({'ok': False, 'erreur': f'Aucun seuil depasse (Temp: {mesure.temperature}C / Hum: {mesure.humidite}%)'})
    try:
        for msg in alertes:
            url  = f"https://api.twilio.com/2010-04-01/Accounts/{seuil.twilio_sid}/Messages.json"
            data = urllib.parse.urlencode({'From': 'whatsapp:+14155238886', 'To': f'whatsapp:{seuil.whatsapp_to}', 'Body': msg}).encode()
            creds = base64.b64encode(f"{seuil.twilio_sid}:{seuil.twilio_token}".encode()).decode()
            req = urllib.request.Request(url, data=data, headers={'Authorization': f'Basic {creds}', 'Content-Type': 'application/x-www-form-urlencoded'})
            urllib.request.urlopen(req, timeout=10)
        return JsonResponse({'ok': True, 'message': " | ".join(alertes)})
    except Exception as e:
        return JsonResponse({'ok': False, 'erreur': str(e)})


def tester_notification(request):
    import urllib.request, urllib.parse, base64
    seuil = Seuil.objects.first()
    if not seuil or not seuil.twilio_sid or not seuil.whatsapp_to:
        return JsonResponse({'ok': False, 'erreur': 'WhatsApp non configuré'})
    try:
        url  = f"https://api.twilio.com/2010-04-01/Accounts/{seuil.twilio_sid}/Messages.json"
        data = urllib.parse.urlencode({'From': 'whatsapp:+14155238886', 'To': f'whatsapp:{seuil.whatsapp_to}', 'Body': 'Test alerte DHT11 - La connexion fonctionne !'}).encode()
        creds = base64.b64encode(f"{seuil.twilio_sid}:{seuil.twilio_token}".encode()).decode()
        req = urllib.request.Request(url, data=data, headers={'Authorization': f'Basic {creds}', 'Content-Type': 'application/x-www-form-urlencoded'})
        urllib.request.urlopen(req, timeout=10)
        return JsonResponse({'ok': True})
    except Exception as e:
        return JsonResponse({'ok': False, 'erreur': str(e)})
