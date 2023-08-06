import random
import string
import requests
import json
from django.conf import settings
from mad_webhooks.models import get_webhook_event_post_attempt_model


def randomString(stringLength=8):
    """Generate a random string of fixed length """
    letters = string.ascii_lowercase
    return ''.join(random.choice(letters) for i in range(stringLength))
