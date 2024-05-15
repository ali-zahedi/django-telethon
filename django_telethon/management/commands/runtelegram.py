import asyncio
import logging
import os
import signal

from django.core.management.base import BaseCommand

from django_telethon.rabbitmq import consume_rabbitmq
from django_telethon.utils import connect_clients, re_connect_clients


async def _run_forever():
    try:
        await connect_clients()
    except Exception as e:
        logging.exception(e, exc_info=True)

    while True:
        await asyncio.sleep(30)
        try:
            await re_connect_clients()
        except KeyboardInterrupt:
            break
        except Exception as e:
            logging.exception(e, exc_info=True)


async def _main():
    loop = asyncio.get_running_loop()

    stop = loop.create_future()

    for s in (signal.SIGINT, signal.SIGTERM):
        loop.add_signal_handler(s, stop.set_result, None)

    task_telegram = asyncio.create_task(_run_forever())
    task_rabbitmq = asyncio.create_task(consume_rabbitmq())

    await stop

    task_telegram.cancel()
    task_rabbitmq.cancel()
    try:
        await task_telegram
        await task_rabbitmq
    except asyncio.CancelledError:
        logging.info("Tasks was cancelled")

    logging.info("Shutting down gracefully")


class Command(BaseCommand):
    help = 'Run telegram'

    def handle(self, *args, **options):
        os.environ["DJANGO_ALLOW_ASYNC_UNSAFE"] = "true"
        asyncio.run(_main())
        os.environ["DJANGO_ALLOW_ASYNC_UNSAFE"] = "false"
        self.stdout.write(self.style.SUCCESS('Successfully finished run telegram client'))
