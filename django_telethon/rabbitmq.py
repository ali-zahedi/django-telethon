import logging

import aio_pika
import pika

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
    except Exception as e:
        logging.exception(f"Failed to process message: {e}")


async def consume_rabbitmq():
    if not RABBITMQ_ACTIVE:
        return

    connection = await aio_pika.connect_robust(RABBITMQ_URL)
    channel = await connection.channel()

    queue = await channel.declare_queue(QUEUE_CHANNEL_NAME, durable=True)

    await queue.consume(process_message)


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
