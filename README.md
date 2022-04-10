<!--![GitHub All Releases](https://img.shields.io/github/downloads/ali-zahedi/django-telethon/total)-->
<!--![GitHub issues](https://img.shields.io/github/issues/ali-zahedi/django-telethon)-->
![GitHub](https://img.shields.io/github/license/ali-zahedi/django-telethon)
![GitHub](https://img.shields.io/pypi/pyversions/django-telethon.svg?maxAge=2592000)
![GitHub](https://img.shields.io/pypi/v/django-telethon.svg?maxAge=2592000)
# Django Telethon config

[[_TOC_]]

This project is to help you use [Telethon](https://docs.telethon.dev/en/stable/index.html). 

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

## Usage


## License

The MIT License (MIT). Please see [License File](LICENSE) for more information.
