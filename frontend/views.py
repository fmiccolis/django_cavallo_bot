from django.shortcuts import render
from django.conf import settings


def index(request):
    context = {
        'settings': settings,
    }
    return render(request, 'index.html', context)

# Create your views here.
