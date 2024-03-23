import asyncio
import logging
import os

from django.core.management.base import BaseCommand

from django_telethon.default_settings import RABBITMQ_ACTIVE
from django_telethon.rabbitmq import connect_rabbitmq
from django_telethon.utils import connect_clients, re_connect_clients


async def _entry_point(proxy):
    try:
        print(f'connecting with: {proxy}')
        await connect_clients(proxy)
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
            await re_connect_clients(proxy)
        except KeyboardInterrupt:
            break
        except Exception as e:
            logging.exception(e, exc_info=True)



class Command(BaseCommand):
    help = 'Run telegram'


    # adding this arguments for using proxy
    def add_arguments(self, parser):
        parser.add_argument('--proxy', type=str, help='Proxy address')
        parser.add_argument('--protocol', type=str, help='proxy protocol')
        parser.add_argument('--port', type=int, help='proxy port')

    
    def handle(self, *args, **options):
        # handle arguments if user use them
        proxy_address = options['proxy'] or None
        protocol = options['protocol'] or 'http'
        port = options['port'] or None
        if not proxy_address is None and not port is None:
            proxy = (protocol, proxy_address, port)
        else:
            proxy = None
            
        os.environ["DJANGO_ALLOW_ASYNC_UNSAFE"] = "true"
        asyncio.run(_entry_point(proxy))
        os.environ["DJANGO_ALLOW_ASYNC_UNSAFE"] = "false"
        self.stdout.write(self.style.SUCCESS('Successfully finished run telegram client'))
