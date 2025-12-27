# Maps URLs for each Django view

from django.urls import path
from . import views

# List of URL patterns for incoming requests
urlpatterns = [
    path('prompt/', views.process_prompt, name='process_prompt'),
    path('models/', views.get_models, name='get_models'),
    path('responses/', views.get_responses, name='get_responses'),
    path('sessions/', views.get_sessions, name='get_sessions'),
    path('sessions/<int:session_id>/', views.get_session, name='get_session'),
] 