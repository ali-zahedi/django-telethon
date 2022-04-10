<!--![GitHub All Releases](https://img.shields.io/github/downloads/ali-zahedi/django-telethon/total)-->
<!--![GitHub issues](https://img.shields.io/github/issues/ali-zahedi/django-telethon)-->
![GitHub](https://img.shields.io/github/license/ali-zahedi/django-telethon)
![GitHub](https://img.shields.io/pypi/pyversions/django-telethon.svg?maxAge=2592000)
![GitHub](https://img.shields.io/pypi/v/django-telethon.svg?maxAge=2592000)
# Django Telethon config

[[_TOC_]]

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
