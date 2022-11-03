from datetime import timedelta

from django.db import models
from django.db.models import Q
from django.utils.timezone import now
from django.utils.translation import gettext_lazy as _

from .sessions import LoginStatus


class LoginQueryset(models.QuerySet):
    def expired(self):
        return self.filter(
            Q(created_at__lt=now() - timedelta(minutes=5)) | Q(client_session__login_status__in=LoginStatus.approve())
        )

    def have_to_send_code(self):
        return self.filter(have_to_send_code=True).distinct('client_session')

    def have_to_login(self):
        return self.filter(Q(code__isnull=False) | Q(bot_token__isnull=False)).distinct('client_session')


class LoginManager(models.Manager):
    def get_queryset(self):
        return LoginQueryset(self.model, using=self._db)

    def remove_old_logins(self):
        return self.all().expired().delete()


class Login(models.Model):
    client_session = models.ForeignKey('ClientSession', on_delete=models.CASCADE, verbose_name=_('Client session'))
    have_to_send_code = models.BooleanField(default=True, verbose_name=_('Have to send code'))
    bot_token = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        verbose_name=_('Bot token'),
    )
    phone_number = models.CharField(
        max_length=20,
        null=True,
        blank=True,
        verbose_name=_('Phone number'),
    )
    code = models.CharField(
        max_length=10,
        null=True,
        blank=True,
        verbose_name=_('Code'),
    )
    passcode = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        verbose_name=_('Passcode'),
    )
    hash_code = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        verbose_name=_('Hash code'),
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_('Created at'),
    )

    objects = LoginManager()

    class Meta:
        verbose_name = _('Login')
        verbose_name_plural = _('Logins')
