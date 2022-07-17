import logging

from telethon import TelegramClient
from telethon.errors import SessionPasswordNeededError

from django_telethon.models import App, ClientSession, Login, LoginStatus
from django_telethon.sessions import DjangoSession
from django_telethon.signals import telegram_client_registered


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
    telegram_client = TelegramClient(DjangoSession(client_session=client_app), app.api_id, app.api_hash)
    await telegram_client.connect()
    if not await telegram_client.is_user_authorized():
        client_app.login_status = LoginStatus.LOGIN_REQUIRED
        client_app.save()
        logging.critical(f"Authorization failed for client: {client_app.name}")
        return
    if client_app.login_status != LoginStatus.LOGIN_DONE:
        client_app.login_status = LoginStatus.LOGIN_DONE
        client_app.save()

    await telegram_client.start()
    telegram_client_registered.send(
        sender=telegram_client.__class__, telegram_client=telegram_client, client_session=client_app
    )


async def connect_clients():
    app = App.objects.first()
    if not app:
        logging.debug("App does not exists.")
        return

    for client in ClientSession.objects.filter(login_status__in=LoginStatus.approve()):
        await connect_client(client, app)


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
    for client in ClientSession.objects.filter(login_status=LoginStatus.LOGIN_WAITING_FOR_TELEGRAM_CLIENT):
        await connect_client(client, app)
