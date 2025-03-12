from channels.generic.websocket import AsyncWebsocketConsumer
import json
from asgiref.sync import sync_to_async
# from .models import Comment, Thread
from django.contrib.auth import get_user_model
import logging

# User = get_user_model()
logger = logging.getLogger(__name__)

# class CommentConsumer(AsyncWebsocketConsumer):
#     async def connect(self):
#         self.thread_slug = self.scope['url_route']['kwargs']['thread_slug']
#         self.room_group_name = f"thread_{self.thread_slug}"

#         # Присоединение к группе
#         await self.channel_layer.group_add(
#             self.room_group_name,
#             self.channel_name
#         )

#         # Принятие подключения
#         await self.accept()

#     async def disconnect(self, close_code):
#         # Отключение от группы
#         await self.channel_layer.group_discard(
#             self.room_group_name,
#             self.channel_name
#         )

#     async def receive(self, text_data):
#         try:
#             # Загружаем данные из текстового сообщения
#             data = json.loads(text_data)
#             content = data.get('content', '').strip()

#             if not content:
#                 return  # Если контент пустой, не отправлять комментарий

#             # Получаем текущего пользователя
#             author = self.scope['user']
#             if not author.is_authenticated:
#                 await self.send(text_data=json.dumps({'error': 'User not authenticated'}))
#                 return

#             # Получаем объект темы
#             thread = await sync_to_async(Thread.objects.get)(slug=self.thread_slug)

#             # Создаем новый комментарий
#             comment = await sync_to_async(Comment.objects.create)(
#                 thread=thread,
#                 author=author,
#                 content=content
#             )

#             # Получаем новое количество комментариев для темы
#             comment_count = await sync_to_async(thread.comments.count)()

#             # Отправляем комментарий в группу
#             await self.channel_layer.group_send(
#                 self.room_group_name,
#                 {
#                     'type': 'send_comment',
#                     'author': author.username,
#                     'content': comment.content,
#                     'created_at': comment.created_at.strftime("%Y-%m-%d %H:%M:%S"),
#                     'id': comment.id,
#                     'comment_count': comment_count,  # Отправка количества комментариев
#                     'is_authenticated': author.is_authenticated  # Добавляем информацию о том, авторизован ли пользователь
#                 }
#             )

#         except Exception as e:
#             logger.error(f"Error in receive method: {e}")
#             await self.send(text_data=json.dumps({
#                 'error': 'An error occurred while processing your request.'
#             }))

#     async def send_comment(self, event):
#         try:
#             # Отправка полученного комментария клиенту
#             await self.send(text_data=json.dumps({
#                 'id': event['id'],
#                 'author': event['author'],
#                 'content': event['content'],
#                 'created_at': event['created_at'],
#                 'comment_count': event['comment_count'],  # Получаем количество комментариев
#                 'is_authenticated': event['is_authenticated']  # Добавляем информацию о пользователе
#             }))
#         except Exception as e:
#             logger.error(f"Error in send_comment method: {e}")



class CommentConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.thread_slug = self.scope['url_route']['kwargs']['thread_slug']
        self.room_group_name = f"thread_{self.thread_slug}"

        # Присоединение к группе
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()

    async def disconnect(self, close_code):
        # Отключение от группы
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        try:
            from .models import Comment, Thread
            User = get_user_model()
            data = json.loads(text_data)
            content = data.get('content', '').strip()
            
            if not content:
                return  # Если контент пустой, не отправлять комментарий

            author = self.scope['user']
            thread = await sync_to_async(Thread.objects.get)(slug=self.thread_slug)

            # Создание нового комментария
            comment = await sync_to_async(Comment.objects.create)(
                thread=thread,
                author=author,
                content=content
            )

            # Получение нового количества комментариев
            comment_count = await sync_to_async(thread.comments.count)()

            # Проверка, является ли текущий пользователь автором комментария
            # is_author = author == comment.author

            # Отправка комментария в группу
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'send_comment',
                    'author': author.username,
                    'content': comment.content,
                    'created_at': comment.created_at.strftime("%Y-%m-%d %H:%M:%S"),
                    'id': comment.id,
                    'comment_count': comment_count,  # Отправка количества комментариев
                    'is_author': comment.author == self.scope['user'] if self.scope['user'].is_authenticated else False,  # Проверка, является ли пользователь автором
                    'is_authenticated': self.scope['user'].is_authenticated,  # Проверка, авторизован ли пользователь
                }
            )

        except Exception as e:
            logger.error(f"Error in receive method: {e}")
            await self.send(text_data=json.dumps({
                'error': 'An error occurred while processing your request.'
            }))

    async def send_comment(self, event):
        try:
            await self.send(text_data=json.dumps({
                'id': event['id'],
                'author': event['author'],
                'content': event['content'],
                'created_at': event['created_at'],
                'comment_count': event['comment_count'],
                'is_author': event['is_author'],  # Получаем информацию о том, является ли пользователь автором
                'is_authenticated': event['is_authenticated'],  # Получаем информацию о том, авторизован ли пользователь
            }))
        except Exception as e:
            logger.error(f"Error in send_comment method: {e}")
