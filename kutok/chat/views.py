from django.shortcuts import render
from .models import ChatMessage

# Create your views here.

# Отображение страницы чата
def chat_page(request):
    messages = ChatMessage.objects.filter(is_deleted=False).order_by('timestamp')
    return render(request, 'chat/general_chat.html', {
        'messages': messages,
    })