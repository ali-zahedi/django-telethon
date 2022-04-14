from django.db import models
from django.utils.translation import gettext_lazy as _


class ClientSession(models.Model):
    name = models.CharField(
        max_length=255,
        verbose_name=_('Client Session Name'),
    )

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = _('Client Session')
        verbose_name_plural = _('Client Sessions')


class Session(models.Model):
    client_session = models.ForeignKey(
        'ClientSession',
        on_delete=models.CASCADE,
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
