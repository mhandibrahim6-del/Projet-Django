from django.urls import path
from .views import dashboard, sauvegarder_seuil, tester_notification
from .api import liste_mesures, derniere_mesure, AjouterMesure

urlpatterns = [
    path('', dashboard),
    path('seuil/sauvegarder/', sauvegarder_seuil),
    path('seuil/tester/', tester_notification),
    path('api/all/', liste_mesures),
    path('api/last/', derniere_mesure),
    path('api/add/', AjouterMesure.as_view()),
]