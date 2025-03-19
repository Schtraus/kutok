from django.contrib import admin
from .models import Category, Thread, Comment, Complaint, Country
from django import forms


# @admin.register(Category)
# class CategoryAdmin(admin.ModelAdmin):
#     list_display = ('name', 'image', 'parent', 'is_active')  # Добавляем поле parent в список отображаемых
#     list_filter = ('is_active', 'parent')  # Добавляем фильтрацию по родительской категории
#     search_fields = ('name',)  # Добавляем поиск по имени и slug категории
#     ordering = ('name',)

#     # Чтобы поле parent отображалось в форме создания/редактирования
#     fields = ('name', 'slug', 'description', 'image', 'is_active', 'parent')  # Указываем порядок полей
#     # Добавляем автоматическое заполнение слага
#     prepopulated_fields = {'slug': ('name',)} 


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'image', 'parent', 'is_active')
    list_filter = ('is_active', 'parent')
    search_fields = ('name',)
    ordering = ('name',)
    fields = ('name', 'slug', 'description', 'image', 'is_active', 'parent')
    prepopulated_fields = {'slug': ('name',)}

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        """Фильтруем поле 'parent', чтобы показывать только категории, у которых уже есть parent"""
        if db_field.name == "parent":
            kwargs["queryset"] = Category.objects.filter(parent__isnull=True)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

@admin.register(Country)
class CountryAdmin(admin.ModelAdmin):
    list_display = ('code', 'name')
    search_fields = ('name',)


@admin.register(Thread)
class ThreadAdmin(admin.ModelAdmin):
    list_display = ('title', 'category',  'author', 'country', 'created_at', 'is_active')
    search_fields = ('title', 'author__username')
    list_filter = ('category', 'country', 'is_active')
    prepopulated_fields = {'slug': ('title',)}


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('thread', 'author', 'created_at', 'updated_at')
    search_fields = ('content', 'author__username')
    list_filter = ('thread',)


@admin.register(Complaint)
class ComplaintAdmin(admin.ModelAdmin):
    list_display = ('id', 'comment', 'user', 'reason', 'status', 'created_at')
    search_fields = ('reason', 'user__username', 'comment__content')
    list_filter = ('status',)
    actions = ['mark_as_reviewed']

    @admin.action(description='Позначити як переглянуті')
    def mark_as_reviewed(self, request, queryset):
        queryset.update(status='reviewed')
