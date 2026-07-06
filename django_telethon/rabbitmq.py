import asyncio
import logging

import aio_pika
import pika
from aio_pika.exceptions import ChannelInvalidStateError

from django_telethon.default_settings import (
    QUEUE_CALLBACK_FN,
    QUEUE_CHANNEL_NAME,
    RABBITMQ_ACTIVE,
    RABBITMQ_URL,
)


__all__ = [
    "send_to_telegra_thread",
]


async def process_message(message: aio_pika.IncomingMessage):
    try:
        async with message.process():
            await QUEUE_CALLBACK_FN(message.body)
    except asyncio.CancelledError:
        raise
    except ChannelInvalidStateError:
        # Raised from message.process().__aexit__ when the underlying channel
        # closed mid-processing. connect_robust will re-establish; ack is lost
        # and the broker will redeliver.
        logging.warning("RabbitMQ channel invalid on ack; message will be redelivered")
    except Exception as e:
        logging.exception(f"Failed to process message: {e}")


async def consume_rabbitmq():
    if not RABBITMQ_ACTIVE:
        logging.warning("RabbitMQ consumer is disabled (RABBITMQ_ACTIVE=False)")
        return

    # Keep local import to avoid top-level import ordering/style conflicts with hooks.
    import asyncio

    while True:
        connection = None
        try:
            logging.info("Connecting RabbitMQ consumer queue=%s", QUEUE_CHANNEL_NAME)
            # heartbeat kept high so long Telethon calls don't trip the broker
            # into closing the channel mid-processing (see redelivery loop notes).
            connection = await aio_pika.connect_robust(RABBITMQ_URL, heartbeat=600)
            channel = await connection.channel()
            # prefetch=1 caps the blast radius of a channel drop to a single
            # un-acked message (and therefore at most one duplicate on reconnect).
            await channel.set_qos(prefetch_count=1)

            queue = await channel.declare_queue(QUEUE_CHANNEL_NAME, durable=True)
            await queue.consume(process_message)
            logging.info("RabbitMQ consumer attached queue=%s", QUEUE_CHANNEL_NAME)

            # Keep this coroutine alive for the lifetime of runtelegram.
            # connect_robust manages reconnects for dropped connections.
            await asyncio.Future()
        except asyncio.CancelledError:
            if connection:
                await connection.close()
            logging.info("RabbitMQ consumer cancelled")
            raise
        except Exception as e:
            logging.exception(f"RabbitMQ consumer failed, retrying in 5s: {e}")
            if connection:
                try:
                    await connection.close()
                except Exception as close_error:
                    logging.exception(f"Failed to close RabbitMQ connection: {close_error}")
            await asyncio.sleep(5)


def send_to_telegra_thread(**payload):
    try:
        parameters = pika.URLParameters(RABBITMQ_URL)
        connection = pika.BlockingConnection(parameters)
        channel = connection.channel()

        channel.queue_declare(queue=QUEUE_CHANNEL_NAME, durable=True)
        byte_payload = str(payload).encode('utf-8')

        channel.basic_publish(
            exchange='',
            routing_key=QUEUE_CHANNEL_NAME,
            body=byte_payload,
            properties=pika.BasicProperties(
                delivery_mode=2,  # Make message persistent
            ),
        )

        connection.close()
    except Exception as e:
        logging.error(f"django telethon error occurred: {e}")
        raise e
