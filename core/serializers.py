from rest_framework import serializers
from .models import Photographer, Event


class EventSerializer(serializers.ModelSerializer):
    class Meta:
        model = Event
        fields = ('id', 'category', 'photographer', 'address', 'name',
                  'description', 'date', 'url', 'code', 'slug', 'is_public', 'status')


class PhotographerSerializer(serializers.ModelSerializer):
    events = EventSerializer(many=True)

    class Meta:
        model = Photographer
        fields = ('id', 'name', 'website', 'instagram',
                  'disk_space', 'slug', 'events', 'status')


class CreatePhotographerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Photographer
        fields = ('name', 'website', 'instagram')
