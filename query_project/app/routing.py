from django.urls import path
from . import consumers

ws_patterns = [
    path('ws/post/<int:pk>/', consumers.MyConsumer.as_asgi())
]