from django.conf import settings

from django_telethon.importer import import_attribute


def get_telethon_config(key, default=None):
    """Fetch configuration from DJANGO_TELETHON in Django settings."""
    return getattr(settings, 'DJANGO_TELETHON', {}).get(key, default)


# Retrieve configuration values
RABBITMQ_ACTIVE = get_telethon_config('RABBITMQ_ACTIVE', False)
RABBITMQ_URL = get_telethon_config('RABBITMQ_URL')
QUEUE_CHANNEL_NAME = get_telethon_config('QUEUE_CHANNEL_NAME')
QUEUE_CALLBACK = get_telethon_config('QUEUE_CALLBACK', default='django_telethon.callback.on_message')
# Maximum seconds a single queue callback may run before its message is nacked.
QUEUE_CALLBACK_TIMEOUT = get_telethon_config('QUEUE_CALLBACK_TIMEOUT', default=300)
# Consecutive connect failures before a session is marked LOGIN_FAILED and
# dropped from the retry loop (re-approve it in the admin to retry).
CLIENT_CONNECT_FAILURE_LIMIT = get_telethon_config('CLIENT_CONNECT_FAILURE_LIMIT', default=10)
QUEUE_CALLBACK_FN = None

# Validate configuration
if RABBITMQ_ACTIVE:
    missing_settings = []

    if not RABBITMQ_URL:
        missing_settings.append('RABBITMQ_URL')
    if not QUEUE_CHANNEL_NAME:
        missing_settings.append('QUEUE_CHANNEL_NAME')

    QUEUE_CALLBACK_FN = import_attribute(QUEUE_CALLBACK)

    if not QUEUE_CALLBACK_FN:
        missing_settings.append('QUEUE_CALLBACK')

    if missing_settings:
        raise ValueError(f"'Telethon' {', '.join(missing_settings)} must be set if RABBITMQ_ACTIVE is True.")
