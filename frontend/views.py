from django.shortcuts import render
from django.conf import settings


def index(request, *args, **kwargs):
    context = {
        'settings': settings,
    }
    return render(request, 'frontend/index.html', context)

# Create your views here.
