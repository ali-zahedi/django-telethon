import logging


async def on_message(byte_string: bytes):
    logging.debug("Received message:", byte_string)
