
from mad_webhooks.models import get_log_model, get_webhook_event_post_attempt_model
from oauth2_provider.models import get_application_model
from mad_webhooks.settings import webhook_settings
import logging
import requests
import json

logger = logging.getLogger(__name__)


class CreateLogClass:
    def __init__(self, status_code, method, path, request_data, response_data, application = None, user = None):
        self.status_code = status_code
        self.method = method
        self.path = path
        self.request_data = request_data
        self.response_data = response_data
        self.application = application
        self.user = user


    def createLog(self):
        if self.application is not None:
            application = get_application_model().objects.get(id=self.application.id)
        else:
            application = None

        log = get_log_model().objects.create(
            status = self.status_code,
            method = self.method,
            path = self.path,
            request_data = self.request_data,
            response_data = self.response_data,
            application = application,
            user = self.user
        )
        return log



class PostEventToWebhookClass:
    def __init__(self, event, webhooks):
        self.event = event
        self.webhooks = webhooks


    def postEventToWebhooks(self):
        # event = Event.objects.get(id=event.id)
        # for each endpoint send the event to the webhook via POST
        webhooks = self.webhooks
        for webhook in webhooks:
            # make query
            query_params = webhook.query_params

            headers = {
                "User-Agent": webhook_settings.WEBHOOK_USER_AGENT
            }
            if webhook.header_params is not None:
                header_params = webhook.header_params
                headers.update(header_params)
            
            # make payload
            payload = {
                "object": self.event.event_object,
                "action": self.event.action,
                "data": str(json.dumps(self.event.event_data)),
            }

            try:
                # send event.data to the webhook endpoint
                send = requests.post(
                    webhook.endpoint_url,
                    data=payload,
                    params=query_params,
                    headers=headers
                )
                r = {
                    'status_code': send.status_code,
                    'text': send.text
                }

                self.event.is_processed = True
                self.event.save()

            except Exception as err:
                r = {
                    'status_code': None,
                    'text': err
                }

            # save post attempt data
            try:
                get_webhook_event_post_attempt_model().objects.create(
                    application = self.event.application,
                    event = self.event,
                    endpoint_url = str(webhook.endpoint_url),
                    status = r['status_code'],
                    response_data = r['text'],
                )
            except Exception as e:
                logger.error("Unable to Post: " + str(e))





# class methods
def createLog(status_code, method, path, request_data, response_data, application = None, user = None):
    create_log = webhook_settings.CREATE_LOG_CLASS(status_code, method, path, request_data, response_data, application, user)
    return create_log.createLog()


def postEventToWebhooks(event, webhooks):
    post_event_to_webhook = webhook_settings.POST_EVENT_TO_WEBHOOK_CLASS(event, webhooks)
    return post_event_to_webhook.postEventToWebhooks()