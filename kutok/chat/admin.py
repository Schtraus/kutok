from django.contrib import admin
from .models import ChatMessage, MessageReport

@admin.register(ChatMessage)
class ChatMessageAdmin(admin.ModelAdmin):
    list_display = ('user', 'message_short', 'timestamp', 'edited_at', 'is_deleted')
    list_filter = ('is_deleted', 'timestamp', 'user')
    search_fields = ('message', 'user__username')
    readonly_fields = ('timestamp',)
    fieldsets = (
        (None, {
            'fields': ('user', 'message', 'timestamp', 'edited_at', 'is_deleted')
        }),
    )

    def message_short(self, obj):
        return obj.message[:50]
    message_short.short_description = 'Message'


@admin.register(MessageReport)
class MessageReportAdmin(admin.ModelAdmin):
    list_display = ('message', 'reported_by', 'reason_short', 'reported_at', 'is_resolved')
    list_filter = ('is_resolved', 'reported_at', 'reported_by')
    search_fields = ('reason', 'reported_by__username', 'message__message')
    readonly_fields = ('reported_at',)
    fieldsets = (
        (None, {
            'fields': ('message', 'reported_by', 'reason', 'reported_at', 'is_resolved')
        }),
    )

    def reason_short(self, obj):
        return obj.reason[:50]
    reason_short.short_description = 'Reason'