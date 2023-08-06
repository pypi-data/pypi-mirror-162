from django.conf import settings
from django.utils.module_loading import import_string
from django.core.exceptions import ImproperlyConfigured
from django.test.signals import setting_changed

USER_SETTINGS = getattr(settings, "MAD_WEBHOOKS", None)

WEBHOOK_MODEL = getattr(settings, "MAD_WEBHOOKS_WEBHOOK_MODEL", "mad_webhooks.Webhook")
EVENT_MODEL = getattr(settings, "MAD_WEBHOOKS_EVENTS_MODEL", "mad_webhooks.Event")
WEBHOOK_EVENT_POST_ATTEMPT_MODEL = getattr(settings, "MAD_WEBHOOKS_WEBHOOK_EVENT_POST_ATTEMPT_MODEL", "mad_webhooks.WebhookEventPostAttempt")
LOG_MODEL = getattr(settings, "MAD_WEBHOOKS_LOG_MODEL", "mad_webhooks.Log")


DEFAULTS = {
    "WEBHOOK_MODEL": WEBHOOK_MODEL,
    "LOG_MODEL": LOG_MODEL,
    "EVENT_MODEL": EVENT_MODEL,
    "WEBHOOK_EVENT_POST_ATTEMPT_MODEL": WEBHOOK_EVENT_POST_ATTEMPT_MODEL,

    "WEBHOOK_ADMIN_CLASS": "mad_webhooks.admin.WebhookAdmin",
    "WEBHOOKS_WEBHOOK_EVENT_POST_ATTEMPT_ADMIN_CLASS": "mad_webhooks.admin.WebhookEventPostAttemptAdmin",
    "EVENT_ADMIN_CLASS": "mad_webhooks.admin.EventAdmin",
    "LOG_ADMIN_CLASS": "mad_webhooks.admin.LogAdmin",

    "GET_USER_TOKEN_CLASS": "mad_webhooks.application.GetUserTokenClass",
    "GET_ACCESS_TOKEN_CLASS": "mad_webhooks.application.GetAccessTokenClass",
    "GET_ACCESS_TOKEN_DETAILS_CLASS": "mad_webhooks.application.GetAccessTokenDetailsClass",
    "GET_APPLICATION_DATA_FROM_REQUEST_CLASS": "mad_webhooks.application.GetApplicationDataFromRequestClass", 
    "GET_WEBHOOK_MIDDLEWARE_CLASS": "mad_webhooks.middleware.Webhook",

    "CREATE_LOG_CLASS": "mad_webhooks.webhook.CreateLogClass",
    "POST_EVENT_TO_WEBHOOK_CLASS": "mad_webhooks.webhook.PostEventToWebhookClass",
    
    "MAKE_EVENT_FROM_LOG_TASK_CLASS": "mad_webhooks.tasks.MakeEventFromLogTaskClass",
    "POST_EVENT_TO_WEBHOOK_TASK_CLASS": "mad_webhooks.tasks.PostEventToWebhookTaskClass",

    "WEBHOOK_USER_AGENT": "mad_webhooks",
}

IMPORT_STRINGS = (
    "LOG_ADMIN_CLASS",
    "EVENT_ADMIN_CLASS",
    "WEBHOOK_ADMIN_CLASS",
    "WEBHOOKS_WEBHOOK_EVENT_POST_ATTEMPT_ADMIN_CLASS",

    "GET_USER_TOKEN_CLASS",
    "GET_ACCESS_TOKEN_CLASS",
    "GET_ACCESS_TOKEN_DETAILS_CLASS",
    "GET_APPLICATION_DATA_FROM_REQUEST_CLASS",
    "GET_WEBHOOK_MIDDLEWARE_CLASS",

    "CREATE_LOG_CLASS",
    "POST_EVENT_TO_WEBHOOK_CLASS",

    "MAKE_EVENT_FROM_LOG_TASK_CLASS",
    "POST_EVENT_TO_WEBHOOK_TASK_CLASS",
)

MANDATORY = IMPORT_STRINGS


def perform_import(val, setting_name):
    """
    If the given setting is a string import notation,
    then perform the necessary import or imports.
    """
    if val is None:
        return None
    elif isinstance(val, str):
        return import_from_string(val, setting_name)
    elif isinstance(val, (list, tuple)):
        return [import_from_string(item, setting_name) for item in val]
    return val


def import_from_string(val, setting_name):
    """
    Attempt to import a class from a string representation.
    """
    try:
        return import_string(val)
    except ImportError as e:
        msg = "Could not import %r for setting %r. %s: %s." % (val, setting_name, e.__class__.__name__, e)
        raise ImportError(msg)



class MadWebhookSettings:

    def __init__(self, user_settings=None, defaults=None, import_strings=None, mandatory=None):
        self._user_settings = user_settings or {}
        self.defaults = defaults or DEFAULTS
        self.import_strings = import_strings or IMPORT_STRINGS
        self.mandatory = mandatory or ()
        self._cached_attrs = set()

    
    @property
    def user_settings(self):
        if not hasattr(self, "_user_settings"):
            self._user_settings = getattr(settings, "MAD_WEBHOOKS", {})
        return self._user_settings


    def __getattr__(self, attr):
        if attr not in self.defaults:
            raise AttributeError("Invalid Mad Webhook setting: %s" % attr)
        
        try:
            # Check if present in user settings
            val = self.user_settings[attr]
        except KeyError:
            val = self.defaults[attr]
        
        if val and attr in self.import_strings:
            val = perform_import(val, attr)
  
        self.validate_setting(attr, val)
        self._cached_attrs.add(attr)
        setattr(self, attr, val)    
        return val


    def validate_setting(self, attr, val):
        if not val and attr in self.mandatory:
            raise AttributeError("mad_webhooks setting: %s is mandatory" % attr)
    
    def reload(self):
        for attr in self._cached_attrs:
            delattr(self, attr)
        self._cached_attrs.clear()
        if hasattr(self, "_user_settings"):
            delattr(self, "_user_settings")

webhook_settings = MadWebhookSettings(USER_SETTINGS, DEFAULTS, IMPORT_STRINGS, MANDATORY)


def reload_mad_webhook_settings(*args, **kwargs):
    setting = kwargs["setting"]
    if setting == "MAD_WEBHOOKS":
        webhook_settings.reload()

setting_changed.connect(reload_mad_webhook_settings)