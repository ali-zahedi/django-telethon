from django.db import models
from django.utils.translation import gettext_lazy as _


class UpdateState(models.Model):
    """
    Model for storing the state of the update process.
    """

    client_session = models.ForeignKey(
        'ClientSession',
        on_delete=models.CASCADE,
        verbose_name=_('Client Session'),
    )
    entity_id = models.BigIntegerField(db_index=True)

    pts = models.IntegerField(
        verbose_name=_('pts'),
    )
    qts = models.IntegerField(
        verbose_name=_('qts'),
    )
    date = models.DateTimeField(
        verbose_name=_('date'),
    )
    seq = models.IntegerField(
        verbose_name=_('seq'),
    )

    class Meta:
        unique_together = (('client_session', 'entity_id'),)
        verbose_name = _('Update state')
        verbose_name_plural = _('Update states')
