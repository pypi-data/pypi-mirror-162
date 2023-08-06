import json

from mad_webhooks.models import Log, get_log_model
from mad_webhooks.settings import webhook_settings
from mad_webhooks.webhook import createLog
from mad_webhooks.application import getApplicationDataFromRequest
# from django.conf import settings

import logging
logger = logging.getLogger(__name__)


class Webhook:
    def __init__(self, get_response):
        self.get_response = get_response
        # One-time configuration and initialization.

    def __call__(self, request):

        # settings.OAUTH2_PROVIDER['PKCE_REQUIRED'] = enforce_public

        # Code to be executed for each request before
        # the view (and later middleware) are called.

        response = self.get_response(request)

        # Code to be executed for each request/response after
        # the view is called.

        try:
            # skip admin
            if "api." in request.META['HTTP_HOST']:
                if request.method not in ('GET', 'HEAD', 'OPTIONS') and response.status_code not in (404, 500, 501):
                    # get application detail
                    app_data = getApplicationDataFromRequest(request)

                    user = app_data['token_user']

                    # prepare request data
                    request_data = {
                        # "header": request.META,
                        "query": request.GET,
                        "body": request.POST,
                    }

                    if request.method == "DELETE":
                        response_body = ""
                    else:
                        response_body = json.loads(response.render().content)

                    # prepare response data
                    response_data = {
                        "body":response_body,
                    }


                    # log data to db
                    createLog(
                        status_code = response.status_code,
                        method = request.method,
                        path = request.path,
                        request_data = request_data,
                        response_data = response_data,
                        application = app_data['application'],
                        user = user
                    )
                    
        except Exception as e:
            # log exception to default logger
            logger.error(str(e))
            
        # return response
        return response


def getWebhookMiddlewareClass(response):
    get_webhook_middleware_class = webhook_settings.GET_WEBHOOK_MIDDLEWARE_CLASS(response)
    return get_webhook_middleware_class