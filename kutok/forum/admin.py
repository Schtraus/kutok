from django.contrib import admin

from .models import Category, Comment, Thread, Complaint

# Register your models here.
@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'is_active')
    prepopulated_fields = {'slug': ('name',)}


@admin.register(Thread)
class ThreadAdmin(admin.ModelAdmin):
    list_display = ('title', 'slug', 'category', 'author', 'created_at', 'is_active')
    list_filter = ('category', 'is_active')
    search_fields = ('title', 'content')
    exclude = ('slug',)


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('thread', 'author', 'created_at')
    list_filter = ('thread',)
    search_fields = ('content',)

@admin.register(Complaint)
class ComplaintAdmin(admin.ModelAdmin):
    list_display = ('comment', 'user', 'reason', 'created_at', 'view_comment_link')  # Добавляем ссылку на комментарий
    list_filter = ('created_at', 'user')
    search_fields = ('reason', 'user__username', 'comment__content')

    def view_comment_link(self, obj):
        """Ссылка на сам комментарий для удобства администрирования"""
        return f'<a href="/admin/app_name/comment/{obj.comment.id}/change/">Перейти к комментарию</a>'
    
    view_comment_link.allow_tags = True
    view_comment_link.short_description = 'Ссылка на комментарий'

    def user_link(self, obj):
        """Ссылка на профиль пользователя"""
        return f'<a href="/admin/auth/user/{obj.user.id}/change/">{obj.user.username}</a>'
    
    user_link.allow_tags = True
    user_link.short_description = 'Автор'