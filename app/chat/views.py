from django.conf import settings
from django.shortcuts import render


def index(request):
    return render(request, 'chat/index.html', {'models': settings.AVAILABLE_MODELS})
