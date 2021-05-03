from django.contrib import admin
from django.urls import reverse
from django.utils.safestring import mark_safe

from core.forms import CategoryForm
from core.models import *


@admin.register(TelegramUser)
class TelegramUserAdmin(admin.ModelAdmin):
    fieldsets = (
        (None, {'fields': ('user', 'username', 'first_name', 'last_name', 'url_encodings', 'url_video', 'status')}),
    )
    list_display = ('username', 'first_name', 'last_name', 'url_video', 'is_photographer', 'status')
    search_fields = ('username', 'first_name', 'last_name')
    list_editable = ('status',)

    def is_photographer(self, telegram_user: TelegramUser):
        if telegram_user.photographer.exists():
            return True
        return False
    is_photographer.short_description = "Fotografo"
    is_photographer.boolean = True


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    fieldsets = (
        (None, {'fields': ('name', 'description', 'emoji', 'status')}),
    )
    list_display = ('name', 'description', 'emoji', 'events_count', 'status')
    search_fields = ('name', 'description')
    list_editable = ('status',)
    form = CategoryForm

    def events_count(self, category: Category):
        events_url = reverse('admin:core_event_changelist')
        events = category.events
        if events.count() > 0:
            return mark_safe(f"<a href='{events_url}?category__id__exact={category.id}'>{events.count()} ({events.exclude(status=False).count()})</a>")
    events_count.short_description = "Eventi (attivi)"


@admin.register(Photographer)
class PhotographerAdmin(admin.ModelAdmin):
    fieldsets = (
        (None, {'fields': ('telegram_user', 'name', 'website', 'instagram', 'slug', 'disk_space', 'status')}),
    )
    list_display = ('name', 'show_website', 'show_insta', 'disk_space', 'events_count', 'status')
    search_fields = ('name', 'website')
    list_editable = ('status',)
    readonly_fields = ('slug',)

    def show_website(self, photographer: Photographer):
        if photographer.website:
            return mark_safe(f'<a href="{photographer.website}" target="_blank">{photographer.website}</a>')
    show_website.short_description = 'Sito web'

    def show_insta(self, photographer: Photographer):
        if photographer.instagram:
            return mark_safe(f'<a href="{settings.INSTAGRAM_BASE_URL.format(photographer.instagram)}" target="_blank">{photographer.instagram}</a>')
    show_insta.short_description = 'Instagram'

    def events_count(self, photographer: Photographer):
        events_url = reverse('admin:core_event_changelist')
        events = photographer.events
        if events.count() > 0:
            return mark_safe(f"<a href='{events_url}?photographer__id__exact={photographer.id}'>{events.count()} ({events.exclude(status=False).count()})</a>")
    events_count.short_description = "Eventi (attivi)"


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    fieldsets = (
        (None, {'fields': ('category', 'photographer', 'address', 'name', 'description', 'url', 'date', 'code', 'slug', ('is_public', 'status'))}),
    )
    list_display = ('name', 'show_url', 'category', 'photographer', 'photos_count', 'date', 'status')
    search_fields = ('name', 'photographer', 'category')
    list_editable = ('status',)
    readonly_fields = ('slug',)
    list_filter = ('category', 'photographer')

    def show_url(self, event: Event):
        return mark_safe(f'<a href="{event.url}" target="_blank">vai all\'album</a>')
    show_url.short_description = 'Album'

    def photos_count(self, event: Event):
        photos_url = reverse('admin:core_photo_changelist')
        photos = event.photos
        if photos.count() > 0:
            return mark_safe(f"<a href='{photos_url}?event__id__exact={event.id}'>{photos.count()} ({photos.exclude(faces='').count()})</a>")
    photos_count.short_description = "Foto (con volti)"


@admin.register(Photo)
class PhotoAdmin(admin.ModelAdmin):
    fieldsets = (
        (None, {'fields': ('event', 'show_url', 'faces', 'status')}),
    )
    list_display = ('url', 'event', 'status')
    search_fields = ('event',)
    list_editable = ('status',)
    readonly_fields = ('show_url',)
    list_filter = ('event', 'event__category')

    def show_url(self, photo: Photo):
        return mark_safe(f'<a href="{photo.url}" target="_blank"><img style="width: 100%" src="{photo.url}" alt="{photo.url}" /></a>')
    show_url.short_description = 'Foto'


@admin.register(PhotoMatch)
class PhotoMatchAdmin(admin.ModelAdmin):
    fieldsets = (
        (None, {'fields': ('photo', 'telegram_user', 'accuracy', 'status')}),
    )
    list_display = ('photo', 'telegram_user', 'accuracy', 'status')
    search_fields = ('telegram_user',)
    list_editable = ('status',)
    list_filter = ('telegram_user', 'photo__event')


admin.site.register(Address)
admin.site.register(Authentication)
admin.site.register(BotMessage)
# Register your models here.
