import os

from setuptools import find_packages, setup

with open(os.path.join(os.path.dirname(__file__), 'README.md'), encoding="utf-8") as readme:
    README = readme.read()

# allow setup.py to be run from any path
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

setup(
    name='django-telethon',
    version='1.0.0',
    packages=find_packages(),
    include_package_data=True,
    license='BSD License',
    description='Telethon for django',
    long_description=README,
    long_description_content_type='text/markdown',
    url='https://github.com/ali-zahedi/django-telethon',
    author='Ali Zahedigol',
    author_email='alizahedigol@gmail.com',
    python_requires='>=3.7',
    classifiers=[
        'Environment :: Web Environment',
        'Framework :: Django',
        'Framework :: Django :: 3.0',
        'Framework :: Django :: 3.1',
        'Framework :: Django :: 3.2',
        'Framework :: Django :: 4.0',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3 :: Only',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
    ],
    install_requires=[
        'Django>=3.0',
        'Telethon>=1.24.0,<2',
    ],
    extras_require={
        'dev': [
            'flake8',
            'black',
            'isort',
            'pre-commit',
            'whitenoise',
        ]
    },
)
