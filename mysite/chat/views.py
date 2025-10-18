from django.shortcuts import render
from .models import Message


def public_chat(request):
    messages = Message.objects.all().order_by('timestamp')[:30]
    return render(request, 'chat/public_chat.html', {'messages': messages})
