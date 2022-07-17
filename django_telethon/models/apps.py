from django.db import models
from django.utils.translation import gettext_lazy as _


class App(models.Model):
    api_id = models.CharField(max_length=255, verbose_name=_('API ID'))
    api_hash = models.CharField(max_length=255, verbose_name=_('API Hash'))

    class Meta:
        verbose_name = _('App')
        verbose_name_plural = _('Apps')
