<!--![GitHub All Releases](https://img.shields.io/github/downloads/ali-zahedi/django-telethon/total)-->
<!--![GitHub issues](https://img.shields.io/github/issues/ali-zahedi/django-telethon)-->
![GitHub](https://img.shields.io/github/license/ali-zahedi/django-telethon)
![GitHub](https://img.shields.io/pypi/pyversions/django-telethon.svg)
![GitHub](https://img.shields.io/pypi/v/django-telethon.svg)
# Django Telethon config


  ⭐️ Thanks **everyone** who has starred the project, it means a lot!

This project is to help you use [Telethon](https://docs.telethon.dev/en/stable/index.html).

Django-Telethon is an asyncio Python 3 MTProto library to interact with Telegram's API as a user or through a bot account (bot API alternative).

### What is this?

Telegram is a popular messaging application. This library is meant to make it easy for you to write Python programs that can interact with Telegram. Think of it as a wrapper that has already done the heavy job for you, so you can focus on developing an application.

Django-Telethon is a session storage implementation backend for Django ORM to use telethon in Django projects.

## Compatibility

* Python 3.7+
* Django 3.0+

## Installation

* Use the following command to install using pip:

```bash
pip install django-telethon
```

**OR**

* You can use the following command to set it up locally so that you can fix bugs or whatever and send pull requests:

```shell script
pip install -e ".[dev]"
pre-commit install
```
For better understanding, please read the:
* [Telethon](https://docs.telethon.dev/en/stable/index.html) documentation.
* [Telethon Session](https://docs.telethon.dev/en/stable/modules/sessions.html) documentation.
* [pre-commit](https://pre-commit.com/docs/installation/) documentation.
* [pip](https://pip.pypa.io/en/stable/installing/) documentation.
* [python package](https://packaging.python.org/en/latest/tutorials/packaging-projects/) documentation.
* [github pull requests](https://help.github.com/en/articles/about-pull-requests/) documentation.

### settings.py


 ``` python
INSTALLED_APPS = [
    # ....
    'django_telethon',
    # ...
]
```
### urls.py

```shell
from django.contrib import admin
from django.urls import path

from django_telethon.urls import django_telethon_urls

admin.autodiscover()

urlpatterns = [
    path('admin/', admin.site.urls),
    path('telegram/', django_telethon_urls()),
]
```
### Migration


```shell script
python manage.py migrate
```

## Signing In

Before working with Telegram’s API, you need to get your own API ID and hash:

- [Login to your Telegram account](https://my.telegram.org/auth) with the phone number of the developer account to use.
- Click under API Development tools.
- Create new application window will appear. Fill in your application details. There is no need to enter any URL, and only the first two fields (App title and Short name) can currently be changed later.
- Click on Create application at the end. Remember that your API hash is secret and Telegram won’t let you revoke it. Don’t post it anywhere!

***This API ID and hash is the one used by your application, not your phone number. You can use this API ID and hash with any phone number or even for bot accounts.***

Read more (proxy, bot and etc) [Here](https://docs.telethon.dev/en/stable/basic/signing-in.html).

## Usage

### Interactive mode

1. Open a terminal and run the following command:

    ```shell script
    python manage.py shell
    ```
1. Enable ```DJANGO_ALLOW_ASYNC_UNSAFE``` in your environment.

    ```python
    import os
    os.environ["DJANGO_ALLOW_ASYNC_UNSAFE"] = "true"
    ```

1. You can import these from ```django_telethon.sessions```. For example, using the ```DjangoSession``` is done as follows:

    ```python
    from telethon.sync import TelegramClient
    from django_telethon.sessions import DjangoSession
    from django_telethon.models import App, ClientSession
    from telethon.errors import SessionPasswordNeededError

    # Use your own values from my.telegram.org
    API_ID = 12345
    API_HASH = '0123456789abcdef0123456789abcdef'

    app, is_created = App.objects.update_or_create(
        api_id=API_ID,
        api_hash=API_HASH
    )
    cs, cs_is_created = ClientSession.objects.update_or_create(
        name='default',
    )
    telegram_client = TelegramClient(DjangoSession(client_session=cs), app.api_id, app.api_hash)
    telegram_client.connect()

    if not telegram_client.is_user_authorized():
        phone = input('Enter your phone number: ')
        telegram_client.send_code_request(phone)
        code = input('Enter the code you received: ')
        try:
            telegram_client.sign_in(phone, code)
        except SessionPasswordNeededError:
            password = input('Enter your password: ')
            telegram_client.sign_in(password=password)
    ```

#### Doing stuffs

```python
print((await telegram_client.get_me()).stringify())

await telegram_client.send_message('username', 'Hello! Talking to you from Telethon')
await telegram_client.send_file('username', '/home/myself/Pictures/holidays.jpg')

await telegram_client.download_profile_photo('me')
messages = await telegram_client.get_messages('username')
await messages[0].download_media()

@telegram_client.on(telegram_client.NewMessage(pattern='(?i)hi|hello'))
async def handler(event):
    await event.respond('Hey!')
```

### API
#### User Login
1. Run the following command to start the server:

    ```shell script
    python manage.py runserver
    ```

1. Run the following command to start telegram client:

    ```shell script
    python manage.py runtelegram
    ```

1. go to [admin panel](http://127.0.0.1:8000/admin/) and [telegram app section](http://127.0.0.1:8000/admin/django_telethon/app/). create a new app. get data from the [your Telegram account](https://my.telegram.org/auth).

1. Request code from telegram:

   ```python
   import requests
   import json

   url = "http://127.0.0.1:8000/telegram/send-code-request/"

   payload = json.dumps({
     "phone_number": "+12345678901",
     "client_session_name": "name of the client session"
   })
   headers = {
     'Content-Type': 'application/json'
   }

   response = requests.request("POST", url, headers=headers, data=payload)

   print(response.text)
    ```

1. Send this request for sign in:

   ```python
   import requests
   import json

   url = "http://127.0.0.1:8000/telegram/login-user-request/"

   payload = json.dumps({
     "phone_number": "+12345678901",
     "client_session_name": "name of the client session",
     "code": "1234",
     "password": "1234"
   })
   headers = {
     'Content-Type': 'application/json'
   }

   response = requests.request("POST", url, headers=headers, data=payload)

   print(response.text)

   ```

#### Bot login
Send this request for sign in:

   ```python
   import requests
   import json

   url = "http://127.0.0.1:8000/telegram/login-bot-request/"

   payload = json.dumps({
     "bot_token": "bot token",
     "client_session_name": "name of the client session",
   })
   headers = {
     'Content-Type': 'application/json'
   }

   response = requests.request("POST", url, headers=headers, data=payload)

   print(response.text)

   ```

### Server-side

If you are using **supervisord** or **another process manager**, you can use the following command to start the server:

```shell script
python manage.py runtelegram
```

#### Supervisord

1. Add the following lines to your ```/etc/supervisord.d/[yourproject].ini``` file:

    ```ini
    [program:telegram_worker]
    directory=/home/projectuser/[your_project_directory]/
    command=/home/projectuser/venv/bin/python manage.py runtelegram
    autostart=true
    autorestart=true
    stderr_logfile=/home/projectuser/logs/telegramworker.err.log
    stdout_logfile=/home/projectuser/logs/telegramworker.out.log
    ```

1. Reload the supervisor daemon:

    ```shell
    supervisorctl reread
    supervisorctl update
    supervisorctl start telegram_worker
    supervisorctl status
    ```

## Listen to events

After login telegram client the signal `telegram_client_registered` is emitted.

1. You can listen to this signal by using the following code for example put this code to your ```receivers.py``` file in app directory:

   ```python
   from functools import partial

   from django.dispatch import receiver
   from telethon import events

   from django_telethon.signals import telegram_client_registered

   async def event_handler(event, client_session):
       print(client_session.name, event.raw_text, sep=' | ')
       # if you need access to telegram client, you can use event.client
       # telegram_client = event.client
       await event.respond('!pong')


   @receiver(telegram_client_registered)
   def receiver_telegram_registered(telegram_client, client_session, *args, **kwargs):
       handler = partial(event_handler, client_session=client_session)
       telegram_client.add_event_handler(
           handler,
           events.NewMessage(incoming=True, pattern='ping'),
       )

   ```

1. In the `apps.py` file, add the following code:

   ```python
   from django.apps import AppConfig

   class MyAppConfig(AppConfig):
       ...

       def ready(self):
           from .receivers import receiver_telegram_registered  # noqa: F401
   ```

1. Read more about signals in [Django signals](https://docs.djangoproject.com/en/4.0/topics/signals/)
1. Read more about events in [Telethon events](https://docs.telethon.dev/en/stable/modules/events.html)



## Django Configuration[Optional]

To configure the Django Telethon library, you need to update your Django settings. Add the following dictionary to your Django settings:

```python
DJANGO_TELETHON = {
    'RABBITMQ_ACTIVE': True or False,   # Set to True if you want to use RabbitMQ. Otherwise, set to False.
    'RABBITMQ_URL': 'your_rabbitmq_url',   # The URL to your RabbitMQ server.
    'QUEUE_CHANNEL_NAME': 'your_channel_name',   # Name of the channel you want to use for the queue.
    'QUEUE_CALLBACK': 'path_to_custom_callback'   # (Optional) Path to your custom callback. Default is 'django_telethon.callback.on_message'.
}
```

#### Example
```python
DJANGO_TELETHON = {
    'RABBITMQ_ACTIVE': True,
    'RABBITMQ_URL': 'amqp://app:app@localhost:5672/app',
    'QUEUE_CHANNEL_NAME': 'EXAMPLE_CHANNEL',   # Name of the channel you want to use for the queue.
    'QUEUE_CALLBACK': 'django_telethon.callback.on_message'   # (Optional) Path to your custom callback. Default is 'django_telethon.callback.on_message'.
}

```

### Default Callback

By default, the library uses a callback `on_message` which logs the received message. If you want to use a custom callback, set the `QUEUE_CALLBACK` in your settings.


## Usage

When a new message arrives at the RabbitMQ channel specified, the configured callback function will be invoked. The default callback logs the message using the Python logging module. You can replace this with your own callback function to process the message as desired.

## Using RabbitMQ for Inter-thread Communication
In the scenario where different parts of your application (like web servers managed by Gunicorn, background workers managed by Celery, etc.) are running on different threads or even different machines, communicating directly might be a challenge. If, for instance, you receive a message directly from Telegram and want to respond or if some event happens on the web front and you wish to notify a Telegram user, it's not straightforward due to these separate threads.

To solve this, Django Telethon library has introduced a mechanism to send messages across threads/machines using RabbitMQ. Here's how you can utilize it:

Connect to RabbitMQ

The library initializes a connection to RabbitMQ and listens for incoming messages. Once a message arrives, the specified callback function is invoked

Sending Messages to Telegram Thread

For components that want to communicate with the Telegram thread, you can use the `send_to_telegra_thread` function. This function sends a message to the Telegram thread via RabbitMQ.

```python
from django_telethon import send_to_telegra_thread

# Send a payload/message to the Telegram thread
send_to_telegra_thread(some_key="some_value", another_key="another_value")
```
The `send_to_telegra_thread` function serializes the payload and sends it to RabbitMQ. The Telegram thread, which is already listening to RabbitMQ, receives this message and can then process it, for example, to send a response back to a Telegram user.

## Callbacks

### Default `on_message` Callback

Here's the default callback provided by the library:

```python
import logging


async def on_message(byte_string: bytes):
    logging.debug("Received message:", byte_string)

```

### Custom Callback

To use a custom callback:

1. Define your custom callback function. Ensure it's an `async` function and has a single parameter of type `aio_pika.IncomingMessage`.
2. Set the `QUEUE_CALLBACK` in `DJANGO_TELETHON` settings to point to your custom callback function's path.

## License

The MIT License (MIT). Please see [License File](LICENSE) for more information.
