from django.urls import path

from .apps import DjangoTelethonConfig
from .views import login_bot_view, login_user_view, send_code_request_view

app_name = DjangoTelethonConfig.name

_urlpatterns = [
    path('send-code-request/', send_code_request_view, name='send_code_request'),
    path('login-user-request/', login_user_view, name='login_user_request'),
    path('login-bot-request/', login_bot_view, name='login_bot_request'),
]


def django_telethon_urls():
    return _urlpatterns, app_name, app_name
