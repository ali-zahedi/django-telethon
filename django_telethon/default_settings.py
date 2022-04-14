"""Default settings for django-telethon."""

import django

if django.__version__ >= '3.0':
    from django.db import models

    TextChoices = models.TextChoices
    IntegerChoices = models.IntegerChoices
else:
    from .models.enum_django import IntegerChoices as InC
    from .models.enum_django import TextChoices as TeC

    TextChoices = TeC
    IntegerChoices = InC
