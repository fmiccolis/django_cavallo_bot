from rest_framework import generics, status
from .serializers import PhotographerSerializer, EventSerializer
from .models import Photographer, Event
from rest_framework.views import APIView
from rest_framework.response import Response


# Create your views here.


class PhotographerView(generics.ListAPIView):
    queryset = Photographer.objects.all()
    serializer_class = PhotographerSerializer


class GetPhotographerSlug(APIView):
    serializer_class = PhotographerSerializer
    lookup_url_kwarg = 'slug'
    class_name = Photographer.my_name()

    def get(self, request, *args, **kwargs):
        slug = kwargs.get(self.lookup_url_kwarg, None)
        if slug:
            photographer = Photographer.objects.filter(slug=slug)
            if len(photographer) > 0:
                data = PhotographerSerializer(photographer[0]).data
                return Response(data, status=status.HTTP_200_OK)
            return Response({f'{self.class_name} Not Found': f'Invalid {self.class_name} {self.lookup_url_kwarg}.'}, status=status.HTTP_404_NOT_FOUND)

        return Response({'Bad Request': f'{self.lookup_url_kwarg} paramater not found in request'}, status=status.HTTP_400_BAD_REQUEST)


class EventView(generics.ListAPIView):
    queryset = Event.objects.all()
    serializer_class = EventSerializer


class GetEventSlug(APIView):
    serializer_class = EventSerializer
    lookup_url_kwarg = 'slug'
    class_name = Event.my_name()

    def get(self, request, *args, **kwargs):
        slug = kwargs.get(self.lookup_url_kwarg, None)
        if slug:
            event = Event.objects.filter(slug=slug)
            if len(event) > 0:
                data = EventSerializer(event[0]).data
                return Response(data, status=status.HTTP_200_OK)
            return Response({f'{self.class_name} Not Found': f'Invalid {self.class_name} {self.lookup_url_kwarg}.'}, status=status.HTTP_404_NOT_FOUND)

        return Response({'Bad Request': f'{self.lookup_url_kwarg} paramater not found in request'}, status=status.HTTP_400_BAD_REQUEST)