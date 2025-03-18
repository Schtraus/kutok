from django.db import models
from django.conf import settings
from django.utils import timezone

class ChatMessage(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='chat_messages')
    message = models.TextField()  # Текст сообщения
    timestamp = models.DateTimeField(auto_now_add=True)  # Время создания
    edited_at = models.DateTimeField(null=True, blank=True)  # Время последнего редактирования
    is_deleted = models.BooleanField(default=False)  # Флаг удаления

    def __str__(self):
        return f'{self.user.username}: {self.message[:20]}'

    class Meta:
        ordering = ['timestamp']  # Сортировка по времени создания


class MessageReport(models.Model):
    message = models.ForeignKey(ChatMessage, on_delete=models.CASCADE, related_name='reports')
    reported_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)  # Кто пожаловался
    reason = models.TextField()  # Причина жалобы
    reported_at = models.DateTimeField(auto_now_add=True)  # Время жалобы
    is_resolved = models.BooleanField(default=False)  # Флаг решения жалобы

    def __str__(self):
        return f'Report on message {self.message.id} by {self.reported_by.username}'