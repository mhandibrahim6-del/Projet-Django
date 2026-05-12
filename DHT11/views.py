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
        seuil.temp_max      = float(request.POST.get('temp_max', 30))
        seuil.humidite_max  = float(request.POST.get('humidite_max', 80))
        seuil.email_from    = request.POST.get('email_from', '').strip()
        seuil.email_password= request.POST.get('email_password', '').strip()
        seuil.email_to      = request.POST.get('email_to', '').strip()
        seuil.save()
    return redirect('/')


def tester_notification(request):
    import smtplib
    from email.mime.text import MIMEText
    seuil = Seuil.objects.first()
    if not seuil or not seuil.email_from or not seuil.email_to:
        return JsonResponse({'ok': False, 'erreur': 'Email non configuré'})
    try:
        msg = MIMEText("Test alerte DHT11 - La connexion fonctionne !", 'plain', 'utf-8')
        msg['Subject'] = 'Test Alerte DHT11'
        msg['From']    = seuil.email_from
        msg['To']      = seuil.email_to
        with smtplib.SMTP_SSL('smtp.gmail.com', 465, timeout=10) as serveur:
            serveur.login(seuil.email_from, seuil.email_password)
            serveur.sendmail(seuil.email_from, seuil.email_to, msg.as_string())
        return JsonResponse({'ok': True})
    except Exception as e:
        return JsonResponse({'ok': False, 'erreur': str(e)})
