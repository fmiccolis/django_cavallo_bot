from django.urls import path
from frontend.views import *


urlpatterns = [
    path('', index, name='index'),
    path('join', index, name='join'),
    path('create', index, name='create')
]
