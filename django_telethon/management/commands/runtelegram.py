import asyncio
import logging
import os

from django.core.management.base import BaseCommand

from django_telethon.default_settings import RABBITMQ_ACTIVE
from django_telethon.rabbitmq import connect_rabbitmq
from django_telethon.utils import connect_clients, re_connect_clients


async def _entry_point():
    try:
        await connect_clients()
    except Exception as e:
        logging.exception(e, exc_info=True)

    while True:
        if RABBITMQ_ACTIVE:
            try:
                await connect_rabbitmq()
            except Exception as e:
                logging.exception(e, exc_info=True)

        await asyncio.sleep(30)
        try:
            await re_connect_clients()
        except KeyboardInterrupt:
            break
        except Exception as e:
            logging.exception(e, exc_info=True)



class Command(BaseCommand):
    help = 'Run telegram'

    def handle(self, *args, **options):
        os.environ["DJANGO_ALLOW_ASYNC_UNSAFE"] = "true"
        asyncio.run(_entry_point())
        os.environ["DJANGO_ALLOW_ASYNC_UNSAFE"] = "false"
        self.stdout.write(self.style.SUCCESS('Successfully finished run telegram client'))
