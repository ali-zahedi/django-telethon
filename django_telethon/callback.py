import logging


async def on_message(body: str):
    logging.debug("Received message:", body)
