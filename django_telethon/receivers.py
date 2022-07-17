from functools import partial

from django.dispatch import receiver
from telethon import events

from django_telethon.signals import telegram_client_registered


async def register_entity(event, client_session):
    # register entity
    await event.get_input_sender()


@receiver(telegram_client_registered)
def receiver_telegram_client_registered(telegram_client, client_session, *args, **kwargs):
    handler = partial(register_entity, client_session=client_session)
    telegram_client.add_event_handler(
        handler,
        events.NewMessage,
    )
