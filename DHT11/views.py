from django.shortcuts import render
from .models import DHT11

def dashboard(request):
    mesure = DHT11.objects.order_by('-date').first()
    return render(request, 'dashboard.html', {'mesure': mesure})