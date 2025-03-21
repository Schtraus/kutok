import json
import logging
from django.utils import timezone
from channels.generic.websocket import AsyncWebsocketConsumer
from django.contrib.auth.models import AnonymousUser
from .models import ChatMessage, MessageReport
from asgiref.sync import sync_to_async
from django.db import transaction

logger = logging.getLogger(__name__)

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        logger.info("WebSocket connection attempt")
        self.room_group_name = 'general_chat'

        # Присоединяем пользователя к группе, даже если он не авторизован
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()
        logger.info("WebSocket connection established")

    async def disconnect(self, close_code):
        try:
            # Отключаем пользователя от группы
            await self.channel_layer.group_discard(
                self.room_group_name,
                self.channel_name
            )
        except Exception as e:
            logger.error(f"Ошибка при отключении WebSocket: {e}")

    async def receive(self, text_data):
        try:
            text_data_json = json.loads(text_data)
            action = text_data_json.get('action')
            user = self.scope['user']
            logger.info(f"Получено действие: {action}, пользователь: {user.username}")  # Логирование

            # Если пользователь не авторизован, разрешаем только чтение
            if isinstance(user, AnonymousUser):
                if action in ['send_message', 'edit_message', 'delete_message', 'report_message']:
                    logger.warning("Неавторизованный пользователь пытается выполнить действие")
                    await self.send(text_data=json.dumps({
                        'error': 'Неавторизованные пользователи могут только читать сообщения.'
                    }))
                    return

            if action == 'send_message':
                message = text_data_json['message']
                chat_message = await self.save_message(user, message)  # Сохраняем сообщение и получаем объект
                if chat_message:  # Проверяем, что chat_message не None
                    timestamp = timezone.now().isoformat()
                    logger.info(f"Таймштамп: {timestamp}")  # Логирование
                    await self.channel_layer.group_send(
                        self.room_group_name,
                        {
                            'type': 'chat_message',
                            'action': 'send_message',
                            'message': message,
                            'user': user.username,
                            'user_id': user.id,
                            'message_id': chat_message.id,  # Добавляем message_id
                            'timestamp': timestamp,
                            'is_author': True,  # Сообщение отправлено текущим пользователем
                        }
                    )
                else:
                    logger.error("Ошибка: chat_message равен None")  # Логирование

            elif action == 'edit_message':
                message_id = text_data_json['message_id']
                new_message = text_data_json['new_message']
                await self.edit_message(user, message_id, new_message)
                await self.channel_layer.group_send(
                    self.room_group_name,
                    {
                        'type': 'chat_message',
                        'action': 'edit_message',
                        'message_id': message_id,
                        'new_message': new_message,
                        'user_id': user.id,
                        'edited_at': timezone.now().isoformat(),
                        'is_author': True,  # Сообщение редактируется текущим пользователем
                    }
                )

            elif action == 'delete_message':
                message_id = text_data_json['message_id']
                await self.delete_message(user, message_id)
                await self.channel_layer.group_send(
                    self.room_group_name,
                    {
                        'type': 'chat_message',
                        'action': 'delete_message',
                        'message_id': message_id,
                        'user_id': user.id,
                        'is_author': True,  # Сообщение удаляется текущим пользователем
                    }
                )

            elif action == 'report_message':
                message_id = text_data_json['message_id']
                reason = text_data_json['reason']
                await self.report_message(user, message_id, reason)
                await self.channel_layer.group_send(
                    self.room_group_name,
                    {
                        'type': 'chat_message',
                        'action': 'report_message',
                        'message_id': message_id,
                        'reason': reason,
                        'user_id': user.id,
                        'is_author': False,  # Жалоба отправляется на сообщение другого пользователя
                    }
                )

        except json.JSONDecodeError:
            logger.error("Ошибка декодирования JSON")
        except Exception as e:
            logger.error(f"Ошибка обработки сообщения: {e}")

    async def chat_message(self, event):
        # Добавляем информацию о текущем пользователе
        current_user = self.scope['user']
        event['current_user_is_author'] = event['user_id'] == current_user.id
        event['is_authenticated'] = not isinstance(current_user, AnonymousUser)
        await self.send(text_data=json.dumps(event))

    @sync_to_async(thread_sensitive=True)
    def save_message(self, user, message):
        try:
            chat_message = ChatMessage.objects.create(user=user, message=message)
            logger.info(f"Сообщение создано: {chat_message.id}")  # Логирование
            return chat_message
        except Exception as e:
            logger.error(f"Ошибка при сохранении сообщения: {e}")  # Логирование
            return None

    @sync_to_async(thread_sensitive=True)
    def edit_message(self, user, message_id, new_message):
        try:
            message = ChatMessage.objects.get(id=message_id)
            if message.user == user:
                message.message = new_message
                message.edited_at = timezone.now()
                message.save()
        except ChatMessage.DoesNotExist:
            logger.warning(f"Попытка редактирования несуществующего сообщения: {message_id}")


    @sync_to_async(thread_sensitive=True)
    def delete_message(self, user, message_id):
        try:
            message = ChatMessage.objects.get(id=message_id)
            if message.user == user:
                message.is_deleted = True 
                message.message = "Сообщение удалено"
                message.save()
        except ChatMessage.DoesNotExist:
            logger.warning(f"Попытка удалить несуществующего сообщения: {message_id}")


    @sync_to_async(thread_sensitive=True)
    def report_message(self, user, message_id, reason):
        try:
            message = ChatMessage.objects.get(id=message_id)
            if message.user != user:
                MessageReport.objects.create(message=message, reported_by=user, reason=reason)
        except ChatMessage.DoesNotExist:
            logger.warning(f"Попытка пожаловаться на несуществующее сообщение: {message_id}")