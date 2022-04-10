"""Default settings for django-telethon."""

import django

if django.__version__ >= '3.0':
    from django.db import models

    TEXT_CHOICES = models.TextChoices
else:
    from .models.enum_django import TextChoices

    TEXT_CHOICES = TextChoices
