from rest_framework import serializers
from .models import Photographer


class PhotographerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Photographer
        fields = ('id', 'name', 'website', 'instagram',
                  'disk_space', 'slug', 'status')


class CreatePhotographerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Photographer
        fields = ('name', 'website', 'instagram')
