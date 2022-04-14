<!--![GitHub All Releases](https://img.shields.io/github/downloads/ali-zahedi/django-telethon/total)-->
<!--![GitHub issues](https://img.shields.io/github/issues/ali-zahedi/django-telethon)-->
![GitHub](https://img.shields.io/github/license/ali-zahedi/django-telethon)
![GitHub](https://img.shields.io/pypi/pyversions/django-telethon.svg?maxAge=2592000)
![GitHub](https://img.shields.io/pypi/v/django-telethon.svg?maxAge=2592000)
# Django Telethon config

[[_TOC_]]

This project is to help you use [Telethon](https://docs.telethon.dev/en/stable/index.html). 

## Compatibility

* Python 3.6+
* Django 2.2+

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

You can import these from ```django_telethon.sessions```. For example, using the ```DjangoSession``` is done as follows:


```python
from telethon.sync import TelegramClient
from django_telethon.sessions import DjangoSession


# Use your own values from my.telegram.org
api_id = 12345
api_hash = '0123456789abcdef0123456789abcdef'

client = TelegramClient(DjangoSession(session_id='3721111111'), api_id, api_hash)
client.connect()

phone = "+3721111111"
if not client.is_user_authorized():
    client.send_code_request(phone)
    client.sign_in(phone, input('Enter the code: '))

```

## License

The MIT License (MIT). Please see [License File](LICENSE) for more information.
