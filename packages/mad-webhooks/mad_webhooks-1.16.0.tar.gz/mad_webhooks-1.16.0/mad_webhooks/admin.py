from mad_webhooks.tasks import postEventToWebhook
from mad_webhooks.models import (
    get_event_admin_class,
    get_log_admin_class,
    get_webhook_admin_class,
    get_webhook_event_post_attempt_admin_class,
    get_webhook_model,
    get_event_model,
    get_webhook_event_post_attempt_model,
    get_log_model,
)
from django.contrib import admin

# Register your models here.


class WebhookAdmin(admin.ModelAdmin):
    ordering = ["-created_at"]
    list_display = ['id', 'application', "endpoint_url", 'is_active', 'created_at']
    raw_id_fields = ['application', ]
    list_filter = ["is_active", "created_at", "updated_at"]
    search_fields = ['application__id', 'application__name', 'endpoint_url']


class WebhookEventPostAttemptAdmin(admin.ModelAdmin):
    ordering = ["-created_at"]
    list_display = ['id', "status", "event", "endpoint_url", 'created_at']
    readonly_fields = list_display + ['response_data', 'event', 'application']
    list_filter = ["status", "created_at", "updated_at"]
    search_fields = ['application__id', 'application__name', 'event__id', 'endpoint_url']

    def has_add_permission(self, request, obj=None):
        return False

class EventAdmin(admin.ModelAdmin):

    def post_event_to_webhook(self, request, queryset):
        for obj in queryset:
            postEventToWebhook.apply_async(
            [obj.id],
            countdown=0
        )
    post_event_to_webhook.short_description = "Post the selected event(s) to webhooks"

    ordering = ["-created_at"]
    list_display = ['id', "event_object", "action", "is_processed", 'log', 'application', 'created_at']
    readonly_fields = list_display + ['event_data', 'application']
    list_filter = ["action", "is_processed", "created_at", "updated_at"]
    actions = [post_event_to_webhook]
    search_fields = ['application__id', 'application__name', 'action', 'event_object', 'log__id', 'id']

    def has_add_permission(self, request, obj=None):
        return False


class LogAdmin(admin.ModelAdmin):
    ordering = ["-created_at"]
    list_display = ['id', "status", "method", "path", 'application', 'created_at']
    raw_id_fields = ['application']
    readonly_fields = list_display + ['request_data', 'response_data', 'user', 'application']
    list_filter = ["status", "method", "created_at", "updated_at"]
    search_fields = ['application__id', 'application__name', 'status', 'path', 'id', 'user__id', 'user__username']

    def has_add_permission(self, request, obj=None):
        return False


# show on admin
webhook_model = get_webhook_model()
webhook_event_post_attempt_model = get_webhook_event_post_attempt_model()
event_model = get_event_model()
log_model = get_log_model()

webhook_admin_class = get_webhook_admin_class()
webhook_event_post_attempt_admin_class = get_webhook_event_post_attempt_admin_class()
event_admin_class = get_event_admin_class()
log_admin_class = get_log_admin_class()

admin.site.register(webhook_model, webhook_admin_class)
admin.site.register(webhook_event_post_attempt_model, webhook_event_post_attempt_admin_class)
admin.site.register(event_model, event_admin_class)
admin.site.register(log_model, log_admin_class)