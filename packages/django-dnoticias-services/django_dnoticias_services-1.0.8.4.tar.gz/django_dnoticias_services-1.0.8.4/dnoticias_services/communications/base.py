from django.conf import settings


class BaseMailRequest:
    API_KEY = getattr(settings, "COMMUNICATIONS_SERVICE_ACCOUNT_API_KEY", None)
    TIMEOUT = getattr(settings, "COMMUNICATIONS_SERVICE_REQUEST_TIMEOUT", 5)

    def __init__(self):
        self.api_key = self.API_KEY
        self.timeout = self.TIMEOUT
