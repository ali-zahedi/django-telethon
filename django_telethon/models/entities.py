from django.db import models
from django.utils.translation import gettext_lazy as _


class Entity(models.Model):
    client_session = models.ForeignKey(
        'ClientSession',
        on_delete=models.SET_NULL,
        null=True,
        verbose_name=_('Client Session'),
    )
    entity_id = models.BigIntegerField(
        verbose_name=_('Entity ID'),
    )
    hash_value = models.BigIntegerField(
        blank=False,
        null=False,
        verbose_name=_('Hash Value'),
    )
    username = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name=_('Username'),
    )
    phone = models.CharField(
        max_length=15,
        blank=True,
        null=True,
        verbose_name=_('Phone'),
    )
    name = models.CharField(
        max_length=150,
        blank=True,
        null=True,
        verbose_name=_('Name'),
    )
    date = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_('Date'),
    )

    class Meta:
        verbose_name = _('Entity')
        verbose_name_plural = _('Entities')
