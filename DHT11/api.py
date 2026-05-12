import smtplib
from email.mime.text import MIMEText
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import generics
from django.utils import timezone
from datetime import timedelta
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


def _envoyer_email(email_from, email_password, email_to, sujet, message):
    msg = MIMEText(message, 'plain', 'utf-8')
    msg['Subject'] = sujet
    msg['From']    = email_from
    msg['To']      = email_to
    with smtplib.SMTP_SSL('smtp.gmail.com', 465, timeout=10) as serveur:
        serveur.login(email_from, email_password)
        serveur.sendmail(email_from, email_to, msg.as_string())


class AjouterMesure(generics.CreateAPIView):
    queryset = DHT11.objects.all()
    serializer_class = DHT11Serializer

    def perform_create(self, serializer):
        instance = serializer.save()
        seuil = Seuil.objects.first()
        if not seuil or not seuil.email_from or not seuil.email_to:
            return

        maintenant = timezone.now()
        cooldown   = timedelta(minutes=5)

        if instance.temperature > seuil.temp_max:
            if not seuil.derniere_alerte_temp or (maintenant - seuil.derniere_alerte_temp) >= cooldown:
                try:
                    _envoyer_email(
                        seuil.email_from, seuil.email_password, seuil.email_to,
                        "ALERTE Temperature DHT11",
                        f"La temperature est {instance.temperature}C et depasse le seuil de {seuil.temp_max}C."
                    )
                    seuil.derniere_alerte_temp = maintenant
                    seuil.save(update_fields=['derniere_alerte_temp'])
                except Exception:
                    pass

        if instance.humidite > seuil.humidite_max:
            if not seuil.derniere_alerte_humid or (maintenant - seuil.derniere_alerte_humid) >= cooldown:
                try:
                    _envoyer_email(
                        seuil.email_from, seuil.email_password, seuil.email_to,
                        "ALERTE Humidite DHT11",
                        f"L'humidite est {instance.humidite}% et depasse le seuil de {seuil.humidite_max}%."
                    )
                    seuil.derniere_alerte_humid = maintenant
                    seuil.save(update_fields=['derniere_alerte_humid'])
                except Exception:
                    pass