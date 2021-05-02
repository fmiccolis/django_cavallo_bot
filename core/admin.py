from django.contrib import admin

from core.models import *


class TelegramUserAdmin(admin.ModelAdmin):
    fieldsets = (
        (None, {'fields': ('username', 'first_name', 'last_name', 'url_encodings', 'url_video', 'status')}),
    )
    list_display = ('username', 'first_name', 'last_name', 'url_video', 'status')
    search_fields = ('username', 'first_name', 'last_name')
    list_editable = ('status',)


admin.site.register(Category)
admin.site.register(Address)
admin.site.register(TelegramUser, TelegramUserAdmin)
admin.site.register(Authentication)
admin.site.register(Photographer)
admin.site.register(Event)
admin.site.register(Photo)
admin.site.register(PhotoMatch)
admin.site.register(BotMessage)
# Register your models here.
