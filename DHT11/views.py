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


def _envoyer_whatsapp_view(sid, token, to, body):
    """Envoie un message WhatsApp via Twilio et retourne (ok, detail)."""
    import urllib.request, urllib.parse, base64, json
    url   = f"https://api.twilio.com/2010-04-01/Accounts/{sid}/Messages.json"
    data  = urllib.parse.urlencode({
        'From': 'whatsapp:+14155238886',
        'To'  : f'whatsapp:{to}',
        'Body': body,
    }).encode()
    creds = base64.b64encode(f"{sid}:{token}".encode()).decode()
    req   = urllib.request.Request(url, data=data, headers={
        'Authorization': f'Basic {creds}',
        'Content-Type' : 'application/x-www-form-urlencoded',
    })
    try:
        resp = urllib.request.urlopen(req, timeout=10)
        return True, json.loads(resp.read().decode()).get('sid', 'OK')
    except urllib.error.HTTPError as e:
        body_err = e.read().decode('utf-8', errors='replace')
        try:
            detail = json.loads(body_err)
            code   = detail.get('code', e.code)
            msg    = detail.get('message', body_err)
            # Messages explicites selon le code Twilio
            if code == 63007:
                msg = "Numéro expéditeur invalide (sandbox Twilio non activé ?)"
            elif code == 63016:
                msg = "Le numéro destinataire n'a pas rejoint le sandbox Twilio. Envoyez le mot-clé join à +14155238886 sur WhatsApp."
            elif code == 63018:
                msg = "Session sandbox expirée. Renvoyez le mot-clé join au +14155238886 sur WhatsApp."
            elif code == 21211:
                msg = f"Numéro WhatsApp invalide : {to}"
            elif code == 20003:
                msg = "Identifiants Twilio incorrects (Account SID ou Auth Token)"
            return False, f"Twilio erreur {code} : {msg}"
        except Exception:
            return False, f"HTTP {e.code} : {body_err[:300]}"
    except Exception as e:
        return False, str(e)


def simuler_alerte(request):
    seuil  = Seuil.objects.first()
    mesure = DHT11.objects.order_by('-date').first()
    if not seuil or not seuil.twilio_sid or not seuil.whatsapp_to:
        return JsonResponse({'ok': False, 'erreur': 'WhatsApp non configuré — remplissez le formulaire ci-dessous'})
    if not mesure:
        return JsonResponse({'ok': False, 'erreur': 'Aucune mesure en base de données'})
    alertes = []
    if mesure.temperature > seuil.temp_max:
        alertes.append(f"🌡 ALERTE DHT11 — Temperature: {mesure.temperature}C depasse le seuil de {seuil.temp_max}C")
    if mesure.humidite > seuil.humidite_max:
        alertes.append(f"💧 ALERTE DHT11 — Humidite: {mesure.humidite}% depasse le seuil de {seuil.humidite_max}%")
    if not alertes:
        return JsonResponse({'ok': False, 'erreur': f'Aucun seuil dépassé — Temp actuelle: {mesure.temperature}°C (seuil: {seuil.temp_max}°C), Humidité: {mesure.humidite}% (seuil: {seuil.humidite_max}%)'})
    erreurs = []
    for msg in alertes:
        ok, detail = _envoyer_whatsapp_view(seuil.twilio_sid, seuil.twilio_token, seuil.whatsapp_to, msg)
        if not ok:
            erreurs.append(detail)
    if erreurs:
        return JsonResponse({'ok': False, 'erreur': erreurs[0]})
    return JsonResponse({'ok': True, 'message': " | ".join(alertes)})


def tester_notification(request):
    seuil = Seuil.objects.first()
    if not seuil or not seuil.twilio_sid or not seuil.whatsapp_to:
        return JsonResponse({'ok': False, 'erreur': 'WhatsApp non configuré — remplissez le formulaire ci-dessous'})
    ok, detail = _envoyer_whatsapp_view(
        seuil.twilio_sid, seuil.twilio_token, seuil.whatsapp_to,
        '✅ Test DHT11 — La connexion WhatsApp fonctionne !'
    )
    if ok:
        return JsonResponse({'ok': True})
    return JsonResponse({'ok': False, 'erreur': detail})
