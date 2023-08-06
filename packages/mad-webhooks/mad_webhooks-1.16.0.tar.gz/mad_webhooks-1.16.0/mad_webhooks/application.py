from django.http import Http404
from rest_framework.authentication import get_authorization_header
from oauth2_provider.models import get_access_token_model, get_application_model
from mad_webhooks.settings import webhook_settings


class GetUserTokenClass:
    def __init__(self, access_token, application):
        self.access_token = access_token
        self.application = application


    def getTokenUser(self):
        access_token = self.access_token
        application = self.application

        if access_token is None:
            user = None
        elif application.authorization_grant_type == 'client-credentials':
            user = None
        else:
            user = access_token.user

        return user


class GetAccessTokenClass:
    def __init__(self, request):
        self.request = request


    def getAccessToken(self):
        request = self.request
        try:
            # return a valid authorization token from request
            return get_authorization_header(request).split()[-1].decode('UTF-8')
        except IndexError as error:
            raise Http404


class GetAccessTokenDetailsClass:
    def __init__(self, token):
            self.token = token

    def getAccessTokenDetails(self):
        token = self.token
        try:
            d = get_access_token_model().objects.get(token=token)
            return d
        except get_access_token_model().DoesNotExist:
            return None


class GetApplicationDataFromRequestClass:
    def __init__(self, request):
        self.request = request


    def getApplicationDataFromRequest(self):
        request = self.request
        try:
            # return a valid authorization token from request
            get_authorization_header(request).split()[-1].decode('UTF-8')

            access_token = getAccessTokenDetails( getAccessToken(request) )
            user = getTokenUser(access_token, access_token.application)

            application_data = {
                "access_token": access_token,
                "application": access_token.application,
                # this is the authorized user who used his user/pass with some client_id/client_secret to access the application
                "token_user": user,
            }
            return application_data

        except IndexError as error:

            application_data = {
                "access_token": None,
                "application": None,
                "token_user": None,
            }

            return application_data

        except AttributeError as ae:
            application_data = {
                "access_token": None,
                "application": None,
                "token_user": None,
            }

            return application_data






# class method calls

def getTokenUser(access_token, application):
    get_user_token_class = webhook_settings.GET_USER_TOKEN_CLASS(access_token, application)
    return get_user_token_class.getTokenUser()



def getAccessToken(request):
    get_access_token_class = webhook_settings.GET_ACCESS_TOKEN_CLASS(request)
    return get_access_token_class.getAccessToken()


def getAccessTokenDetails(token):
    get_access_token_details_class = webhook_settings.GET_ACCESS_TOKEN_DETAILS_CLASS(token)
    return get_access_token_details_class.getAccessTokenDetails()


def getApplicationDataFromRequest(request):
    get_application_data_from_request = webhook_settings.GET_APPLICATION_DATA_FROM_REQUEST_CLASS(request)
    return get_application_data_from_request.getApplicationDataFromRequest()
