from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class DjangoTelethonConfig(AppConfig):
    name = 'django_telethon'
    verbose_name = _('Django Telethon')
    verbose_name_plural = _('Django Telethon')
    default_auto_field = 'django.db.models.BigAutoField'

    def ready(self):
        from .receivers import receiver_telegram_client_registered  # noqa: F401
