from django.db import models
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _
from oauth2_provider.settings import oauth2_settings
from django.apps import apps
from mad_webhooks.settings import webhook_settings


# Create your models here.


class WebhookAbstract(models.Model):
    id = models.BigAutoField(unique=True, primary_key=True)
    application = models.ForeignKey(oauth2_settings.APPLICATION_MODEL, on_delete=models.SET_NULL, null=True, blank=True, verbose_name=_('Application'))
    endpoint_url = models.CharField(max_length=500, verbose_name=_('Webhook Endpoint'), blank=False, null=False, help_text="Webhook URI - URI where the system will send the payload.")
    query_params = models.JSONField(_('Query Parameters'), default=dict, blank=True, null=True, help_text="These parameters will be sent back to the webhook endpoint via query string.")
    header_params = models.JSONField(_('Header Parameters'), default=dict, blank=True, null=True, help_text="These parameters will be sent back to the webhook endpoint via request header.")
    description = models.TextField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)

    class Meta:
        abstract = True
        ordering = ['-created_at']
        verbose_name = _('Webhook Endpoint')
        verbose_name_plural = _('Webhook Endpoints')

    def __str__(self):
        return "Webhook ID: " + str(self.id)

class Webhook(WebhookAbstract):
    pass



class LogAbstract(models.Model):
    id = models.BigAutoField(unique=True, primary_key=True)
    application = models.ForeignKey(oauth2_settings.APPLICATION_MODEL, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Created By Application")
    user = models.ForeignKey(get_user_model(), on_delete=models.SET_NULL, null=True, verbose_name=_("Users"), help_text="Activity was preformed by this user")
    request_data = models.JSONField(_('Request Data'), default=dict, blank=True, null=True)
    response_data = models.JSONField(_('Response Data'), default=dict, blank=True, null=True)
    path = models.CharField(_('Path'), max_length=500, blank=False, null=False)
    status = models.CharField(_('HTTP Status'), max_length=255, blank=False, null=False)
    method = models.CharField(_('HTTP Method'), max_length=255, blank=False, null=False)
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)

    class Meta:
        abstract = True
        ordering = ['-created_at']

    def __str__(self):
        return "Log ID: " + str(self.id)

class Log(LogAbstract):
    pass


class EventAbstract(models.Model):
    id = models.BigAutoField(unique=True, primary_key=True)
    application = models.ForeignKey(oauth2_settings.APPLICATION_MODEL, on_delete=models.SET_NULL, null=True, blank=True, verbose_name=_('Application'))
    event_object = models.CharField(max_length=500, blank=True, null=True, help_text="")
    action = models.CharField(max_length=50, blank=True, null=True, help_text="create/update/partial-update/delete etc")
    event_data = models.JSONField(_('Event Data'), default=dict, blank=True, null=True, help_text="Payload to be sent to webhook endpoint")
    is_processed = models.BooleanField(default=False, help_text="Whether the event has been posted to webhook endpoints or not")
    log = models.ForeignKey(Log, on_delete=models.SET_NULL, null=True, blank=True, verbose_name=_('Log'))
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)

    class Meta:
        abstract = True
        ordering = ['-created_at']

    def __str__(self):
        return "Event ID: " + str(self.id)

class Event(EventAbstract):
    pass


class WebhookEventPostAttemptAbstract(models.Model):
    id = models.BigAutoField(unique=True, primary_key=True)
    application = models.ForeignKey(oauth2_settings.APPLICATION_MODEL, on_delete=models.SET_NULL, null=True, blank=True, verbose_name=_('Application'))
    event = models.ForeignKey(Event, on_delete=models.SET_NULL, null=True, blank=True, verbose_name=_('Event'))
    endpoint_url = models.CharField(max_length=255, verbose_name=_('Webhook Endpoint'), blank=False, null=False)
    status = models.CharField(_('HTTP Status'), max_length=10, blank=True, null=True)
    response_data = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)

    class Meta:
        abstract = True
        ordering = ['-created_at']

    def __str__(self):
        return "Webhook Post Attempt ID: " + str(self.id)

class WebhookEventPostAttempt(WebhookEventPostAttemptAbstract):
    pass




## Model methods
def get_webhook_model():
    """Return the Webhook model that is active in this project."""
    return apps.get_model(webhook_settings.WEBHOOK_MODEL)


def get_event_model():
    """Return the Event model that is active in this project."""
    return apps.get_model(webhook_settings.EVENT_MODEL)


def get_webhook_event_post_attempt_model():
    """Return the Webhook event post attempt model that is active in this project."""
    return apps.get_model(webhook_settings.WEBHOOK_EVENT_POST_ATTEMPT_MODEL)


def get_log_model():
    """Return the Log model that is active in this project."""
    return apps.get_model(webhook_settings.LOG_MODEL)


## Admin classes
def get_webhook_admin_class():
    """Return the Webhook admin class that is active in this project."""
    webhook_admin_class = webhook_settings.WEBHOOK_ADMIN_CLASS
    return webhook_admin_class


def get_event_admin_class():
    """Return the Event admin class that is active in this project."""
    event_admin_class = webhook_settings.EVENT_ADMIN_CLASS
    return event_admin_class


def get_log_admin_class():
    """Return the Log admin class that is active in this project."""
    log_admin_class = webhook_settings.LOG_ADMIN_CLASS
    return log_admin_class


def get_webhook_event_post_attempt_admin_class():
    """Return the Webhook event post attempt admin class that is active in this project."""
    wepa_admin_class = webhook_settings.WEBHOOKS_WEBHOOK_EVENT_POST_ATTEMPT_ADMIN_CLASS
    return wepa_admin_class