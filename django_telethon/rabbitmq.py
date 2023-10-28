import logging

import aio_pika
import pika

from django_telethon.default_settings import RABBITMQ_URL, QUEUE_CHANNEL_NAME, QUEUE_CALLBACK_FN

_rabbit_registered = False


async def connect_rabbitmq():
    global _rabbit_registered

    if _rabbit_registered:
        return

    _rabbit_registered = True

    connection = await aio_pika.connect_robust(
        RABBITMQ_URL
    )

    # Creating a channel
    channel = await connection.channel()

    # Declare a queue to make sure it exists. If the queue is already there this won't do anything.
    queue = await channel.declare_queue(QUEUE_CHANNEL_NAME, durable=True)

    # Creating a consumer callback
    async def on_message(message: aio_pika.IncomingMessage):
        async with message.process():
            await QUEUE_CALLBACK_FN(message.body)

    await queue.consume(on_message)


def send_to_telegra_thread(**payload):
    try:
        parameters = pika.URLParameters(RABBITMQ_URL)
        connection = pika.BlockingConnection(parameters)
        channel = connection.channel()

        # Ensure the queue exists. You might want to move this outside the function if you know the queue already exists.
        channel.queue_declare(queue=QUEUE_CHANNEL_NAME, durable=True)
        byte_payload = str(payload).encode('utf-8')
        # Send the message
        channel.basic_publish(
            exchange='',
            routing_key=QUEUE_CHANNEL_NAME,
            body=byte_payload,
            properties=pika.BasicProperties(
                delivery_mode=2,  # Make message persistent
            ))

        connection.close()
    except Exception as e:
        logging.error(f"django telethon error occurred: {e}")
        raise e
