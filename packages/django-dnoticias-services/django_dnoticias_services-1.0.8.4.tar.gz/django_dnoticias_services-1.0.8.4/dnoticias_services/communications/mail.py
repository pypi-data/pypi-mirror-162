import http
import json
from typing import Iterable, Optional
import requests

from django.http import HttpRequest
from django.conf import settings

from dnoticias_services.communications.base import BaseMailRequest
from dnoticias_services.utils.request import get_headers


class SendEmail(BaseMailRequest):
    def __call__(
        self,
        email: str,
        template_uuid: str,
        brand_group_uuid: str,
        subject: str,
        context: Optional[dict] = dict(),
        from_email: Optional[str] = None,
        from_name: Optional[str] = None,
        attachments: Optional[list] = [],
        track_opens: Optional[bool] = True,
        track_clicks: Optional[bool] = True,
        api_key: Optional[str] = None,
        timeout: Optional[int] = None
    ) -> requests.Response:
        """
        Send an email to a single recipient.

        :parameter email: The recipient's email address.
        :parameter template_uuid: The UUID of the template to use.
        :parameter brand_group_uuid: The UUID of the brand group to use.
        :parameter subject: The subject of the email.
        :parameter context: The context to use when rendering the template.
        :parameter from_email: The email address to use as the sender.
        :parameter from_name: The name to use as the sender.
        :parameter attachments: A list of attachments to send with the email.
        :parameter track_opens: Whether to track when the email is opened.
        :parameter track_clicks: Whether to track when the email is clicked.
        :parameter api_key: The API key to use.
        :parameter timeout: The timeout to use when making the request.
        :return: The response from the request.
        :rtype: requests.Response
        :raises requests.exceptions.RequestException: If the request fails.
        :raises requests.exceptions.HTTPError: If the request fails.
        :raises requests.exceptions.ConnectionError: If the request fails.
        :raises requests.exceptions.Timeout: If the request fails.
        """
        url = settings.COMMUNICATIONS_SEND_EMAIL_API_URL
        _api_key = api_key or self.api_key
        _timeout = timeout or self.timeout

        response = requests.post(
            url,
            headers=get_headers(_api_key),
            json={
                "email" : email,
                "template_uuid" : template_uuid,
                "brand_group_uuid" : brand_group_uuid,
                "subject" : subject,
                "context" : context,
                "from_email" : from_email,
                "from_name" : from_name,
                "attachments" : attachments,
                "track_opens" : track_opens,
                "track_clicks" : track_clicks,
            },
            timeout=_timeout
        )
        response.raise_for_status()
        return response


class SendEmailBulk(BaseMailRequest):
    def __call__(
        self,
        emails: Optional[Iterable[str]] = [],
        template_uuid: Optional[str] = None,
        brand_group_uuid: Optional[str] = None,
        subject: Optional[str] = "",
        subjects: Optional[list] = [],
        context: Optional[list] = list(),
        from_email: Optional[str] = None,
        from_name: Optional[str] = None,
        attachments: Optional[list] = [],
        track_opens: Optional[bool] = True, 
        track_clicks: Optional[bool] = True,
        api_key: Optional[str] = None,
        timeout: Optional[int] = None
    ) -> requests.Response:
        """Send emails in bulk. If you want to send emails with different subjects, you can pass a 
        list of subjects into the 'subjects' parameter and leave 'subject' empty.

        :parameter emails: List of emails to send the email to.
        :parameter template_uuid: UUID of the template to use.
        :parameter brand_group_uuid: UUID of the brand group to use.
        :parameter subject: Subject of the email.
        :parameter subjects: List of subjects to use for each email.
        :parameter context: Context to use for the email.
        :parameter from_email: From email to use.
        :parameter from_name: From name to use.
        :parameter attachments: List of attachments to use.
        :parameter track_opens: Whether to track opens.
        :parameter track_clicks: Whether to track clicks.
        :parameter api_key: API key to use.
        :parameter timeout: Timeout to use.
        :return: Response from the server.
        :rtype: requests.Response
        :raises: requests.HTTPError
        :raises: requests.Timeout
        :raises: requests.RequestException
        """
        url = settings.COMMUNICATIONS_SEND_EMAIL_BULK_API_URL
        _api_key = api_key or self.api_key
        _timeout = timeout or self.timeout

        response = requests.post(
            url,
            headers=get_headers(_api_key),
            json={
                "emails" : emails,
                "template_uuid" : template_uuid,
                "brand_group_uuid" : brand_group_uuid,
                "subject" : subject,
                "subjects" : subjects,
                "context" : context,
                "from_email" : from_email,
                "from_name" : from_name,
                "attachments" : attachments,
                "track_opens" : track_opens,
                "track_clicks" : track_clicks,
            },
            timeout=_timeout
        )

        response.raise_for_status()

        return response


class GetUserEmailList(BaseMailRequest):
    """
    Gets the user email list from dnoticias-mail service.
    """
    def __call__(self, user_id: int, api_key: Optional[str] = None) -> requests.Response:
        """Get the user email list from dnoticias-mail service.

        :parameter user_id: The user id.
        :parameter api_key: The API key to use.
        :return: The response from the request.
        :rtype: requests.Response
        :raises requests.exceptions.RequestException: If the request fails.
        :raises requests.exceptions.HTTPError: If the request fails.
        :raises requests.exceptions.ConnectionError: If the request fails.
        :raises requests.exceptions.Timeout: If the request fails.
        """
        _api_key = api_key or self.api_key

        response = requests.get(
            settings.COMMUNICATIONS_EMAIL_USER_LIST_API_URL.format(user_id),
            headers=get_headers(_api_key),
        )

        response.raise_for_status()

        return response


class GetUserDatatableEmailList(BaseMailRequest):
    """
    Gets the user email datatable from dnoticias-mail service.
    """
    def __call__(
        self,
        request: HttpRequest,
        user_email: str,
        api_key: Optional[str] = None
    ) -> requests.Response:
        """Get the user email datatable from dnoticias-mail service.

        :parameter request: The request object.
        :parameter user_email: The user email.
        :parameter api_key: The API key to use.
        :return: The response from the request.
        :rtype: requests.Response
        :raises requests.exceptions.RequestException: If the request fails.
        :raises requests.exceptions.HTTPError: If the request fails.
        :raises requests.exceptions.ConnectionError: If the request fails.
        :raises requests.exceptions.Timeout: If the request fails.
        """
        _api_key = api_key or self.api_key

        request = json.dumps(request.POST)
        
        response = requests.post(
            settings.COMMUNICATIONS_EMAIL_USER_DATATABLE_LIST_API_URL.format(user_email),
            headers=get_headers(_api_key),
            json=request,
        )

        response.raise_for_status()

        return response


get_user_email_list = GetUserEmailList()
send_email_bulk = SendEmailBulk()
send_email = SendEmail()
get_user_datatable_email_list = GetUserDatatableEmailList()


__all__ = ("send_email", "send_email_bulk", "get_user_email_list", "get_user_datatable_email_list")
