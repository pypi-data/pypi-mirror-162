from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class WebhooksConfig(AppConfig):
    name = 'mad_webhooks'
    verbose_name = 'Webhooks'

    def ready(self):
        import mad_webhooks.signals