from channels.generic.websocket import AsyncWebsocketConsumer
from asgiref.sync import sync_to_async
from django.contrib.auth.models import AnonymousUser
from .models import Comment, Thread
from django.core.exceptions import PermissionDenied
from datetime import datetime, timezone
import json

class CommentConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.thread_id = self.scope['url_route']['kwargs']['thread_id']
        self.room_group_name = f'thread_{self.thread_id}'

        self.user = self.scope['user']
        self.is_authenticated = not isinstance(self.user, AnonymousUser) and self.user.is_authenticated

        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        await self.accept()

        # Отправляем информацию о авторизации клиенту
        await self.send(text_data=json.dumps({
            'action': 'auth_status',
            'is_authenticated': self.is_authenticated,
            'username': self.user.username if self.is_authenticated else None
        }))



    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        data = json.loads(text_data)
        action = data.get('action')
        user = self.scope.get('user')

        if not user or isinstance(user, AnonymousUser):
            print("Ошибка: пользователь не аутентифицирован")
            return  # Игнорируем запрос, если пользователь не авторизован
        
        
        if action == 'add_comment':
            await self.add_comment(data, user)
        elif action == 'edit_thread':
            await self.edit_thread(data, user)
        elif action == 'edit_comment':
            await self.edit_comment(data, user)
        elif action == 'delete_comment':
            await self.delete_comment(data, user)
        elif action == 'report_comment':
            await self.report_comment(data, user)
    
    async def edit_thread(self, data, user):
        thread_id = data.get('thread_id')
        new_content = data.get('content')

        try:
            thread = await Thread.objects.aget(id=thread_id)

            # Проверяем, что пользователь является автором треда
            thread_author = await sync_to_async(lambda: thread.author)()
            if thread_author != user:
                raise PermissionDenied("Вы не можете редактировать этот тред.")

            # Обновляем только контент треда
            thread.content = new_content
            await thread.asave()

            # Отправляем обновленный контент всем пользователям
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'update_thread',
                    'thread_id': thread_id,
                    'content': new_content
                }
            )

        except Thread.DoesNotExist:
            print(f"Тред с ID {thread_id} не найден")
        except PermissionDenied as e:
            print(f"Ошибка: {e}")
    


    async def add_comment(self, data, user):
        content = data.get('content')
        thread_id = data.get('thread_id')

        thread = await Thread.objects.aget(id=thread_id)
        comment = await Comment.objects.acreate(
            thread=thread,
            author=user,
            content=content
        )

        comment_count = await Comment.objects.filter(thread_id=thread_id).acount()

        # Сериализуем комментарий перед отправкой
        serialized_comment = await self.serialize_comment(comment)

        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'new_comment',
                'comment': serialized_comment,
                'comment_count': comment_count,
            }
        )

    async def edit_comment(self, data, user):
        comment_id = data.get('comment_id')
        new_content = data.get('content')

        if not new_content:
            return

        try:
            comment = await Comment.objects.aget(id=comment_id)

            # Получаем автора в асинхронном контексте
            comment_author = await sync_to_async(lambda: comment.author)()

            if comment_author != user:
                raise PermissionDenied("Вы не можете редактировать этот комментарий.")

            comment.content = new_content
            await comment.asave()

            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'update_comment',
                    'comment': await self.serialize_comment(comment)
                }
            )

        except Comment.DoesNotExist:
            print(f"Комментарий с ID {comment_id} не найден")


    async def delete_comment(self, data, user):
        """
        Обрабатывает запрос на удаление комментария от клиента.
        """
        comment_id = data.get('comment_id')
        thread_id = data.get('thread_id')

        if not comment_id or not thread_id:
            print("Ошибка: отсутствует comment_id или thread_id")
            return

        try:
            comment = await Comment.objects.aget(id=comment_id)

            # Получаем автора в асинхронном контексте
            comment_author = await sync_to_async(lambda: comment.author)()

            if comment_author != user:
                print("Ошибка: пользователь не аутентифицирован")
                raise PermissionDenied("Вы не можете удалить этот комментарий.")

            await comment.adelete()
            comment_count = await Comment.objects.filter(thread_id=thread_id).acount()

            # Уведомляем всех клиентов об удалении комментария
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'handle_delete_comment',  # Используем новый метод
                    'comment_id': comment_id,
                    'comment_count': comment_count
                }
            )

        except Comment.DoesNotExist:
            print(f"Комментарий с ID {comment_id} не найден")

    async def handle_delete_comment(self, event):
        """
        Обрабатывает уведомление об удалении комментария и отправляет его клиенту.
        """
        await self.send(text_data=json.dumps({
            'action': 'delete_comment',
            'comment_id': event['comment_id'],
            'comment_count': event['comment_count']
        }))


    async def report_comment(self, data, user):
        comment_id = data.get('comment_id')
        reason = data.get('reason')

        print(f"Пользователь {user.username} пожаловался на комментарий {comment_id}. Причина: {reason}")

    async def serialize_comment(self, comment):
        current_user = self.scope['user']
        is_authenticated = not isinstance(current_user, AnonymousUser) and current_user.is_authenticated
        is_author = is_authenticated and current_user == comment.author
        return {
            'id': comment.id,
            'author': comment.author.username,
            'content': comment.content,
            'created_at': await sync_to_async(lambda: comment.created_at.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"))(),
            'avatar_url': await sync_to_async(lambda: comment.author.profile.avatar.url if hasattr(comment.author, 'profile') else '')(),
            "is_authenticated": is_authenticated,
            "is_author": is_author,
        }

    async def new_comment(self, event):
        await self.send(text_data=json.dumps({
            'action': 'new_comment',
            'comment': event['comment'],
            'comment_count': event['comment_count'],
        }))

    async def update_comment(self, event):
        """
        Отправляет обновленный комментарий клиенту.
        """
        await self.send(text_data=json.dumps({
            'action': 'update_comment',
            'comment': event['comment']
        }))
    
    async def update_thread(self, event):
        """
        Обрабатывает сообщение об обновлении треда и отправляет его клиенту.
        """
        await self.send(text_data=json.dumps({
            'action': 'update_thread',
            'thread_id': event['thread_id'],
            'content': event['content']
        }))


