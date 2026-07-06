import logging

from telethon import TelegramClient
from telethon.errors import SessionPasswordNeededError

from django_telethon.default_settings import CLIENT_CONNECT_FAILURE_LIMIT
from django_telethon.models import App, ClientSession, Login, LoginStatus
from django_telethon.sessions import DjangoSession
from django_telethon.signals import telegram_client_registered


# Live TelegramClient instances keyed by ClientSession.pk. Prevents a second
# connect_client() call for an already-connected session from spawning a
# duplicate client (and duplicate event handlers in host apps).
connected_clients: dict = {}

# Consecutive connect failures per ClientSession.pk. In-memory on purpose:
# a process restart grants a fresh set of attempts.
connect_failures: dict = {}


def _record_connect_failure(client_app):
    count = connect_failures.get(client_app.pk, 0) + 1
    connect_failures[client_app.pk] = count
    if count < CLIENT_CONNECT_FAILURE_LIMIT:
        return
    connect_failures.pop(client_app.pk, None)
    client_app.login_status = LoginStatus.LOGIN_FAILED
    client_app.save(update_fields=['login_status'])
    logging.critical(
        f"Client {client_app.name} failed to connect {count} times in a row; "
        "marked LOGIN_FAILED - re-approve it in the admin to retry."
    )


async def login_bot(client_session, bot_token):
    app = App.objects.first()
    if not app:
        raise ValueError("App does not exists.")
    telegram_client = TelegramClient(DjangoSession(client_session=client_session), app.api_id, app.api_hash)
    await telegram_client.connect()
    await telegram_client.sign_in(bot_token=bot_token)
    result = await telegram_client.is_user_authorized()
    await telegram_client.disconnect()
    return result


async def login_user(client_session, phone_number, code, password, phone_code_hash):
    app = App.objects.first()
    if not app:
        raise ValueError("App does not exists.")
    telegram_client = TelegramClient(DjangoSession(client_session=client_session), app.api_id, app.api_hash)
    await telegram_client.connect()
    try:
        await telegram_client.sign_in(phone=phone_number, code=code, phone_code_hash=phone_code_hash)
    except SessionPasswordNeededError:
        await telegram_client.sign_in(password=password)
    result = await telegram_client.is_user_authorized()
    await telegram_client.disconnect()
    return result


async def send_code_request(client_session, phone_number):
    app = App.objects.first()
    if not app:
        raise ValueError("App does not exists.")
    telegram_client = TelegramClient(DjangoSession(client_session=client_session), app.api_id, app.api_hash)
    await telegram_client.connect()
    result = await telegram_client.send_code_request(phone_number)
    await telegram_client.disconnect()
    return result.phone_code_hash


async def connect_client(client_app, app):
    existing_client = connected_clients.get(client_app.pk)
    if existing_client is not None:
        if existing_client.is_connected():
            connect_failures.pop(client_app.pk, None)
            logging.debug(f"Client already connected, skipping: {client_app.name}")
            return
        # Stale entry (disconnected); is_connected() is also False while telethon
        # auto-reconnects, so disconnect the old instance for real before
        # replacing it — otherwise its reconnect could revive a duplicate client.
        connected_clients.pop(client_app.pk, None)
        try:
            await existing_client.disconnect()
        except Exception:
            logging.exception(f"Failed to disconnect stale client: {client_app.name}")
    telegram_client = TelegramClient(DjangoSession(client_session=client_app), app.api_id, app.api_hash)
    await telegram_client.connect()
    try:
        if not await telegram_client.is_user_authorized():
            client_app.login_status = LoginStatus.LOGIN_REQUIRED
            client_app.save(update_fields=['login_status'])
            if hasattr(client_app, 'session'):
                client_app.session.delete()
            logging.critical(f"Authorization failed for client: {client_app.name}")
            await telegram_client.disconnect()
            return
        if client_app.login_status != LoginStatus.LOGIN_DONE:
            client_app.login_status = LoginStatus.LOGIN_DONE
            client_app.save()

        await telegram_client.start()
    except Exception:
        # Never leave a connected but unregistered client behind: the retry
        # loop would open a new connection every cycle and leak the old ones.
        try:
            await telegram_client.disconnect()
        except Exception:
            logging.exception(f"Failed to disconnect client after setup error: {client_app.name}")
        raise
    connected_clients[client_app.pk] = telegram_client
    connect_failures.pop(client_app.pk, None)
    telegram_client_registered.send(
        sender=telegram_client.__class__, telegram_client=telegram_client, client_session=client_app
    )


async def connect_clients():
    app = App.objects.first()
    if not app:
        logging.debug("App does not exists.")
        return

    for client in ClientSession.objects.filter(login_status__in=LoginStatus.approve()):
        try:
            await connect_client(client, app)
        except Exception:
            logging.exception(f"Failed to connect client: {client.name}")
            _record_connect_failure(client)


async def re_connect_clients():
    app = App.objects.first()
    if not app:
        logging.debug("App does not exists.")
        return
    Login.objects.remove_old_logins()
    # sends code
    for login in Login.objects.all().have_to_send_code():
        phone_hash = await send_code_request(login.client_session, login.phone_number)
        login.hash_code = phone_hash
        login.have_to_send_code = False
        login.save()
    # logs in
    for login in Login.objects.all().have_to_login():
        if login.bot_token:
            login_result = await login_bot(login.client_session, login.bot_token)
        else:
            login_result = await login_user(
                login.client_session, login.phone_number, login.code, login.passcode, login.hash_code
            )
        if login_result:
            login.client_session.login_status = LoginStatus.LOGIN_WAITING_FOR_TELEGRAM_CLIENT
            login.client_session.save()
            logging.debug(f"Login successfully for client: {login.client_session.name}")
        else:
            logging.debug(f"Login failed for client: {login.client_session.name}")
        login.delete()
    # Reconnect every approved session, not only the ones waiting for a client:
    # a LOGIN_DONE session whose initial connect failed must be retried too.
    # The connected_clients registry makes this idempotent for live sessions.
    for client in ClientSession.objects.filter(login_status__in=LoginStatus.approve()):
        try:
            await connect_client(client, app)
        except Exception:
            logging.exception(f"Failed to reconnect client: {client.name}")
            _record_connect_failure(client)
