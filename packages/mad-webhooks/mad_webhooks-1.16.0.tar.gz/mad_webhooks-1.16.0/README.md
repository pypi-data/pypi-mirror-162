# Mad Webhooks


Mad webooks app for django to webhooks to the user

## Quick start

Add "mad_webhooks" to your INSTALLED_APPS setting like this:

```python
INSTALLED_APPS = [
    ...
    'mad_webhooks',
]
```

Include the middlewre at the end in your settings like this:

```python
MIDDLEWARE = [
    ...
    "mad_webhooks.middleware.getWebhookMiddlewareClass",
]
```

Run ``python manage.py migrate`` to create mad_webhooks models.

## Overriding Default Classes

### Update your project settings

```python
"MAD_WEBHOOKS_WEBHOOK_MODEL": "mad_webhooks.Webhook",
"MAD_WEBHOOKS_EVENTS_MODEL": "mad_webhooks.Event",
"MAD_WEBHOOKS_WEBHOOK_EVENT_POST_ATTEMPT_MODEL": "mad_webhooks.WebhookEventPostAttempt",
"MAD_WEBHOOKS_LOG_MODEL": "mad_webhooks.Log",

MAD_WEBHOOKS = {
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
    "POST_EVENT_TO_WEBHOOK_CLASS": "mad_webhooks.webhook.PostEventToWebhookClass"
}
```

see existing class for override reference.
