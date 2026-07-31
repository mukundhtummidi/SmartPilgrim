from django.urls import path
from . import views

app_name = 'crowd_ai'

urlpatterns = [
    path('chat/', views.chatbot_view, name='chatbot'),
    path('api/chat/', views.chatbot_api, name='chatbot_api'),
]
