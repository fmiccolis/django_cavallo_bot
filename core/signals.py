from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver

from core.models import Photographer, Event, Photo


@receiver(post_save, sender=Photographer)
def toggle_events_state(sender, instance, created, **kwargs):
    if not created:
        update_fields = kwargs.get('update_fields', None)
        if update_fields:
            if 'status' in update_fields:
                if not instance.status:
                    events = Event.objects.filter(photographer=instance)
                    for event in events:
                        event.status = False
                    Event.objects.bulk_update(events, ['status'])


@receiver(post_delete, sender=Photo)
def delete_old_encodings(sender, instance: Photo, **kwargs):
    faces = instance.faces
    if faces and hasattr(faces, 'storage') and hasattr(faces, 'path'):
        storage_, path_ = faces.storage, faces.path
        storage_.delete(path_)
