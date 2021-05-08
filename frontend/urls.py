from django.urls import path
from frontend.views import *


urlpatterns = [
    path('', index, name='index'),
    path('photographer/<slug:slug>', index, name='join'),
    path('create', index, name='create')
]
