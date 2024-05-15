from django.contrib import admin, messages

from . import send_to_telegra_thread
from .models import App, ClientSession, Entity, Login, SentFile, Session, UpdateState


@admin.register(App)
class AppAdmin(admin.ModelAdmin):
    list_display = (
        'api_id',
        'api_hash',
    )


@admin.register(ClientSession)
class ClientSessionAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'login_status']
    list_filter = ('login_status',)


@admin.register(Login)
class LoginAdmin(admin.ModelAdmin):
    list_display = [
        'id',
        'client_session',
        'have_to_send_code',
        'bot_token',
        'phone_number',
        'code',
        'passcode',
        'hash_code',
        'created_at',
    ]
    list_filter = ['created_at', 'client_session__name']


@admin.register(Session)
class SessionAdmin(admin.ModelAdmin):
    list_display = [
        'client_session',
        'auth_key',
        'data_center_id',
        'port',
        'server_address',
        'takeout_id',
    ]
    raw_id_fields = ['client_session']
    list_filter = ['client_session__name']


@admin.register(Entity)
class EntityAdmin(admin.ModelAdmin):
    list_display = [
        'pk',
        'entity_id',
        'client_session',
        'hash_value',
        'username',
        'phone',
        'name',
        'date',
    ]
    raw_id_fields = ['client_session']
    list_filter = ['client_session__name']
    search_fields = (
        'hash_value',
        'entity_id',
        'username',
        'phone',
        'name',
    )
    actions = ('send_a_test_message',)

    @admin.action(description="Send a test message")
    def send_a_test_message(self, request, queryset):
        queryset = queryset.select_related('client_session')
        for entity in queryset:
            entity_id = entity.entity_id
            # TODO: try to handle this method inside the package
            payload = {
                'fn': 'send_message',
                'msg': f'Check **{entity}**',
                'parser': 'md',
                'sender_name': entity.client_session.name,
                'receiver_id': entity_id,
                'file_path': None,
            }
            send_to_telegra_thread(**payload)
        messages.success(request, f"Successfully sent message to {queryset.count()} entities.")


@admin.register(UpdateState)
class UpdateStateAdmin(admin.ModelAdmin):
    list_display = [
        'id',
        'client_session',
        'pts',
        'qts',
        'date',
        'seq',
    ]
    raw_id_fields = ['client_session']
    list_filter = ['client_session__name']


@admin.register(SentFile)
class SentFileAdmin(admin.ModelAdmin):
    list_display = [
        'id',
        'client_session',
        'md5_digest',
        'file_size',
        'file_type',
        'hash_value',
        'file_id',
    ]
    raw_id_fields = ['client_session']
    list_filter = ['client_session__name']
