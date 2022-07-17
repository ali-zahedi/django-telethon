from django.db import models
from django.db.models import IntegerChoices
from django.utils.translation import gettext_lazy as _
from telethon.tl.types import InputDocument, InputPhoto


class SentFileType(IntegerChoices):
    DOCUMENT = 0
    PHOTO = 1

    @staticmethod
    def from_type(cls):
        if cls == InputDocument:
            return SentFileType.DOCUMENT
        elif cls == InputPhoto:
            return SentFileType.PHOTO
        else:
            raise ValueError('The cls must be either InputDocument/InputPhoto')


class SentFile(models.Model):
    client_session = models.ForeignKey(
        'ClientSession',
        on_delete=models.CASCADE,
        verbose_name=_('Client Session'),
    )
    md5_digest = models.BinaryField(
        verbose_name=_('MD5 digest'),
    )
    file_size = models.IntegerField(
        verbose_name=_('File size'),
    )
    file_type = models.IntegerField(
        choices=SentFileType.choices,
        verbose_name=_('Type'),
    )
    hash_value = models.BigIntegerField(
        verbose_name=_('Hash value'),
    )
    file_id = models.IntegerField(
        verbose_name=_('File ID'),
    )

    class Meta:
        unique_together = (
            (
                'client_session',
                'md5_digest',
                'file_size',
                'file_type',
            ),
        )
        verbose_name = _('Sent file')
        verbose_name_plural = _('Sent files')
