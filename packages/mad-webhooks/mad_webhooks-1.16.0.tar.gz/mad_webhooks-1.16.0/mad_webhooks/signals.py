

from django.db.models.signals import post_save
from django.dispatch import receiver

from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from mad_webhooks.models import get_log_model, get_event_model

from mad_webhooks.tasks import makeEventFromLogTask



@receiver(post_save, sender=get_log_model())
def LogPostSaveSignal(sender, instance, created, **kwargs):
    """
    Receive signal on webhook event and add it to queue
    """
    if created is True:
        makeEventFromLogTask.apply_async(
            [instance.id],
            countdown=0
        )
