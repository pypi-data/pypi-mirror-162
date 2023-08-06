from mad_webhooks.webhook import postEventToWebhooks
from mad_webhooks.models import get_event_model, get_log_model, get_webhook_model
from celery import shared_task

from mad_webhooks.settings import webhook_settings


class MakeEventFromLogTaskClass:
    def __init__(self, log_id):
        self.log_id = log_id
    
    def makeEventFromLogTask(self):
        log_id = self.log_id
        # get log
        log = get_log_model().objects.get(id=log_id)

        if int(log.status) in (200, 201, 202, 204):
            # make event from log
            # set action
            action = ''
            if log.method == 'POST':
                action = "create"
            if log.method == 'PUT':
                action = "update"
            if log.method == 'PATCH':
                action = "partial_update"
            if log.method == 'DELETE':
                action = "delete"

            # set event object
            event_object = log.path[1:-1]

            # set payload
            event_data = {
                "request": {
                    "query": log.request_data['query'],
                    "body": log.request_data['body']
                },
                "response": log.response_data['body']
            }

            application = log.application

            # save to db
            event = get_event_model().objects.create(
                application = application,
                action = action,
                event_object = event_object,
                event_data = event_data,
                log = log,
            )
            # call task to process the event.
            postEventToWebhook.apply_async(
                [event.id],
                countdown=0
            )
            return "Event ID: " + str(event.id) +" successfully generated from Log ID: " + str(log.id)

        else:
            return "No event was generated from Log ID: " + str(log.id)


class PostEventToWebhookTaskClass:
    def __init__(self, event_id):
        self.event_id = event_id


    def postEventToWebhook(self):
        event_id = self.event_id
        """ Post the event to webhook """
        # get event Details
        event = get_event_model().objects.get(id=event_id)

        # post to application webhooks
        if event.application is not None:
            # get webhook endpoint urls from application
            webhooks = get_webhook_model().objects.filter(application=event.application, is_active=True)
            postEventToWebhooks(event, webhooks)

        return "Processed event " + str(event.id)


@shared_task(name="Non-Periodic: Post Event to Webhooks", soft_time_limit=50000, time_limit=80000)
def postEventToWebhook(event_id):
    post_event_to_webhook = webhook_settings.POST_EVENT_TO_WEBHOOK_TASK_CLASS(event_id)
    return post_event_to_webhook.postEventToWebhook()


@shared_task(name="Non-Periodic: Make Event from Log")
def makeEventFromLogTask(log_id):
    make_event_from_log_task = webhook_settings.MAKE_EVENT_FROM_LOG_TASK_CLASS(log_id)
    return make_event_from_log_task.makeEventFromLogTask()