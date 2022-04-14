from django.contrib import admin

from .models import ClientSession, Entity, SentFile, Session, UpdateState


class ClientSessionAdmin(admin.ModelAdmin):
    list_display = [
        'id',
        'name',
    ]


class SessionAdmin(admin.ModelAdmin):
    list_display = [
        'id',
        'client_session',
        'data_center_id',
        'port',
        'server_address',
        'takeout_id',
    ]


class EntityAdmin(admin.ModelAdmin):
    list_display = [
        'id',
        'client_session',
        'username',
        'phone',
        'name',
        'date',
    ]


class UpdateStateAdmin(admin.ModelAdmin):
    list_display = [
        'id',
        'client_session',
        'pts',
        'qts',
        'date',
        'seq',
    ]


class SentFileAdmin(admin.ModelAdmin):
    list_display = ['id', 'client_session', 'file_size', 'file_type', 'file_id']


admin.site.register(ClientSession, ClientSessionAdmin)
admin.site.register(Session, SessionAdmin)
admin.site.register(Entity, EntityAdmin)
admin.site.register(UpdateState, UpdateStateAdmin)
admin.site.register(SentFile)
