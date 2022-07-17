import django.dispatch

# providing_args = ["telegram_client", "client_session"]
telegram_client_registered = django.dispatch.Signal()
