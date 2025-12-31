# Maps URLs for each Django view

from django.urls import path
from . import views

# List of URL patterns for incoming requests
urlpatterns = [
    path('', views.index, name='index'),
    path('chat/', views.chat, name='chat'),
]
