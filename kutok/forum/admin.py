from django.contrib import admin

from .models import Category, Comment, Thread

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