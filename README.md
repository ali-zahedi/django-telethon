<!--![GitHub All Releases](https://img.shields.io/github/downloads/ali-zahedi/django-telethon/total)-->
<!--![GitHub issues](https://img.shields.io/github/issues/ali-zahedi/django-telethon)-->
![GitHub](https://img.shields.io/github/license/ali-zahedi/django-telethon)
![GitHub](https://img.shields.io/pypi/pyversions/django-telethon.svg)
![GitHub](https://img.shields.io/pypi/v/django-telethon.svg)
# Django Telethon config


  ⭐️ Thanks **everyone** who has starred the project, it means a lot!

This project is to help you use [Telethon](https://docs.telethon.dev/en/stable/index.html). 

Djagno-Telethon is an asyncio Python 3 MTProto library to interact with Telegram's API as a user or through a bot account (bot API alternative).

###What is this?

Telegram is a popular messaging application. This library is meant to make it easy for you to write Python programs that can interact with Telegram. Think of it as a wrapper that has already done the heavy job for you, so you can focus on developing an application.

A Django-Telethon session storage implementation backed for Django ORM to use telethon in django projects.

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

[Login to your Telegram account](https://my.telegram.org/auth) with the phone number of the developer account to use.
Click under API Development tools.
A Create new application window will appear. Fill in your application details. There is no need to enter any URL, and only the first two fields (App title and Short name) can currently be changed later.
Click on Create application at the end. Remember that your API hash is secret and Telegram won’t let you revoke it. Don’t post it anywhere!

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
    cs = ClientSession.objects.update_or_create(
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

#### Doing stuff

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
1. run the following command to start the server:

    ```shell script
    python manage.py runserver
    ```

1. run the following command to start telegram client:

    ```shell script
    python manage.py runtelegram
    ```
   
1. go to [admin panel](http://127.0.0.1:8000/admin/) and [telegram app section](http://127.0.0.1:8000/admin/django_telethon/app/). create a new app. get data from the [your Telegram account](https://my.telegram.org/auth).

1. request code from telegram:
    
   ```python
   import requests
   import json
   
   url = "127.0.0.1:8000/telegram/send-code-request/"
   
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

1. send this request for sign in:
    
   ```python
   import requests
   import json
   
   url = "127.0.0.1:8000/telegram/login-user-request/"
   
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
send this request for sign in:
    
   ```python
   import requests
   import json
   
   url = "127.0.0.1:8000/telegram/login-bot-request/"
   
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

1. you can listen to this signal by using the following code for example put this code to your ```receivers.py``` file in app directory:
   
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
           events.NewMessage(pattern='ping'),
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

## License

The MIT License (MIT). Please see [License File](LICENSE) for more information.
