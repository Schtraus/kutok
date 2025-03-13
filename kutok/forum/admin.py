from django.contrib import admin
from .models import Category, Thread, Comment, Complaint, Country


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'is_active')
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ('name',)
    list_filter = ('is_active',)


# @admin.register(Subcategory)
# class SubcategoryAdmin(admin.ModelAdmin):
#     list_display = ('name', 'slug', 'category', 'is_active')
#     prepopulated_fields = {'slug': ('name',)}
#     search_fields = ('name', 'category__name')
#     list_filter = ('category', 'is_active')


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
    list_display = ('comment', 'user', 'reason', 'status', 'created_at')
    search_fields = ('reason', 'user__username', 'comment__content')
    list_filter = ('status',)
    actions = ['mark_as_reviewed']

    @admin.action(description='Позначити як переглянуті')
    def mark_as_reviewed(self, request, queryset):
        queryset.update(status='reviewed')
