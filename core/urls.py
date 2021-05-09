from django.urls import path
from .views import PhotographerView, GetPhotographerSlug, EventView, GetEventSlug

urlpatterns = [
    path('photographer/all', PhotographerView.as_view()),
    path('photographer/<slug:slug>', GetPhotographerSlug.as_view()),
    path('event/all', EventView.as_view()),
    path('event/<slug:slug>', GetEventSlug.as_view()),
]
