import django.dispatch

receive_event = django.dispatch.Signal(providing_args=["data"])