from django.contrib import admin, messages

from . import send_to_telegra_thread
from .models import App, ClientSession, Entity, Login, SentFile, Session, UpdateState


@admin.register(App)
class AppAdmin(admin.ModelAdmin):
    # api_hash is credential material; list only a masked indicator. It stays
    # on the form because the form is how the credentials are entered.
    list_display = (
        'api_id',
        'has_api_hash',
    )

    @admin.display(boolean=True, description='Has API hash')
    def has_api_hash(self, obj):
        return bool(obj.api_hash)


@admin.register(ClientSession)
class ClientSessionAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'login_status']
    list_filter = ('login_status',)


@admin.register(Login)
class LoginAdmin(admin.ModelAdmin):
    # bot_token/passcode/hash_code are credentials; list only masked indicators.
    list_display = [
        'id',
        'client_session',
        'have_to_send_code',
        'has_bot_token',
        'phone_number',
        'has_code',
        'has_passcode',
        'has_hash_code',
        'created_at',
    ]
    list_filter = ['created_at', 'client_session__name']
    raw_id_fields = ('client_session',)

    def get_exclude(self, request, obj=None):
        # hash_code is machine-written (never hand-entered) and bot_token only
        # matters at creation; keep them off the forms so stored credentials
        # can't be read back. code/passcode stay editable for the manual
        # user-login flow (enter received code + 2FA password).
        exclude = ('hash_code',)
        if obj is not None:
            exclude += ('bot_token',)
        return exclude

    @admin.display(boolean=True, description='Has bot token')
    def has_bot_token(self, obj):
        return bool(obj.bot_token)

    @admin.display(boolean=True, description='Has code')
    def has_code(self, obj):
        return bool(obj.code)

    @admin.display(boolean=True, description='Has passcode')
    def has_passcode(self, obj):
        return bool(obj.passcode)

    @admin.display(boolean=True, description='Has hash code')
    def has_hash_code(self, obj):
        return bool(obj.hash_code)


@admin.register(Session)
class SessionAdmin(admin.ModelAdmin):
    # auth_key is MTProto session-hijack material; never render it in the admin,
    # neither in the list nor on the change form (it is machine-written only).
    exclude = ('auth_key',)
    list_display = [
        'client_session',
        'has_auth_key',
        'data_center_id',
        'port',
        'server_address',
        'takeout_id',
    ]
    raw_id_fields = ['client_session']
    list_filter = ['client_session__name']

    @admin.display(boolean=True, description='Has auth key')
    def has_auth_key(self, obj):
        return bool(obj.auth_key)


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
        'pk',
        'client_session',
        'entity_id',
        'pts',
        'qts',
        'date',
        'seq',
    ]
    raw_id_fields = ['client_session']
    list_filter = ['client_session__name']

    @admin.display(description="client session")
    def client_session(self, obj):
        return obj.client_session.name

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        return queryset.select_related('client_session')


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
