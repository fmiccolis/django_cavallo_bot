from django.urls import path
from .views import PhotographerView, GetPhotographerSlug

urlpatterns = [
    path('photographers', PhotographerView.as_view()),
    path('photographer/<slug:slug>', GetPhotographerSlug.as_view()),
]
