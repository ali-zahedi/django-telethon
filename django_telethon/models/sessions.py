from django.db import models
from django.utils.translation import gettext_lazy as _


class LoginStatus(models.IntegerChoices):
    LOGIN_REQUIRED = 1
    LOGIN_DONE = 2
    LOGIN_FAILED = 3
    LOGIN_WAITING_FOR_TELEGRAM_CLIENT = 4

    @classmethod
    def approve(cls) -> list:
        return [cls.LOGIN_DONE.value, cls.LOGIN_WAITING_FOR_TELEGRAM_CLIENT.value]


class ClientSession(models.Model):
    name = models.CharField(
        max_length=255,
        verbose_name=_('Client Session Name'),
    )
    login_status = models.PositiveSmallIntegerField(
        default=LoginStatus.LOGIN_REQUIRED,
        choices=LoginStatus.choices,
        verbose_name=_('Login Required'),
    )

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = _('Client Session')
        verbose_name_plural = _('Client Sessions')


class Session(models.Model):
    client_session = models.OneToOneField(
        'ClientSession',
        on_delete=models.CASCADE,
        primary_key=True,
        verbose_name=_('Client Session'),
    )
    auth_key = models.BinaryField(
        blank=False,
        null=False,
        editable=True,
        verbose_name=_('Auth Key'),
    )
    data_center_id = models.IntegerField(
        db_index=True,
        verbose_name=_('Data Center ID'),
    )
    port = models.IntegerField(
        verbose_name=_('Port'),
    )
    server_address = models.CharField(
        max_length=255,
        verbose_name=_('Server Address'),
    )
    takeout_id = models.BigIntegerField(
        null=True,
        verbose_name=_('Takeout ID'),
    )

    class Meta:
        unique_together = (
            (
                'client_session_id',
                'data_center_id',
            ),
        )
        verbose_name = _('Session')
        verbose_name_plural = _('Sessions')
