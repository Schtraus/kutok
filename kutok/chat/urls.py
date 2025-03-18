from . import views
from django.urls import path

app_name = 'chat'

urlpatterns = [
    path('general-chat/', views.chat_page, name='general_chat'),
]
