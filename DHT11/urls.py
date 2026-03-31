from django.urls import path
from .views import dashboard
from .api import liste_mesures, derniere_mesure, AjouterMesure

urlpatterns = [
    path('', dashboard),
    path('api/all/', liste_mesures),
    path('api/last/', derniere_mesure),
    path('api/add/', AjouterMesure.as_view()),
]