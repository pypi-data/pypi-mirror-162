from datetime import datetime
from typing import Dict, Iterable, Optional

from django.conf import settings

import requests

from dnoticias_services.communications.base import BaseMailRequest
from dnoticias_services.utils.request import get_headers


"""
SETTINGS:

CREATE_NOTIFICATION_API_URL
NOTIFICATION_API_URL
DELETE_NOTIFICATION_API_URL
GET_NOTIFICATION_LIST_API_URL
CREATE_TOPIC_API_URL
GET_TOPICS_SELECT2_API_URL
GET_TOPIC_LIST_API_URL
TOPIC_API_URL
"""

class Notifications(BaseMailRequest):
    APPLICATION_HEADER = "X-FCM-APPLICATION-DOMAIN"

    @classmethod
    def __generate_headers(cls, api_key: str) -> Dict[str, str]:
        """Generates the header dict for every request made to communications

        :parameter api_key: Application API key
        :return: request headers
        :rtype: dict
        """
        headers = get_headers(api_key)
        headers.update({cls.APPLICATION_HEADER: settings.NOTIFICATIONS_APPLICATION_DOMAIN})
        return headers

    @classmethod
    def create_notification(
        cls,
        object_id: str,
        content_type_id: str,
        title: str,
        icon_url: str,
        image_url: str,
        redirect_url_web: str,
        redirect_url_app: str,
        body: Optional[str] = None,
        to_send: Optional[bool] = False,
        scheduled_for: Optional[datetime] = None, 
        topics: Optional[Iterable[str]] = None,
        api_key: Optional[str] = None,
        timeout: Optional[int] = None
    ) -> requests.Response:
        """Creates a new notification on communications system

        :parameter object_id: Object ID related to the notification in the application
        :parameter content_type_id: Content type ID related to the object associated to the notif.
        :parameter title: Notification title
        :parameter body: Notification body
        :parameter icon_url: Notification icon absolute URL
        :parameter image_url: Notification image absolute URL
        :parameter redirect_url_web: Redirect URL used in browser notifications
        :parameter redirect_url_app: Redirect URL used in application notifications
        :parameter to_send: True if the notification will be send after saved
        :parameter scheduled_for: Datetime that the notification will be send
        :parameter topics: Topics associated to the notification
        :parameter api_key: API Key, optional
        :parameter timeout: request timeout, optional
        :return: Response from communications
        :rtype: requests.Response
        """
        _api_key = api_key or cls.API_KEY
        _timeout = timeout or cls.TIMEOUT

        response = requests.post(
            settings.CREATE_NOTIFICATION_API_URL,
            headers=cls.__generate_headers(_api_key),
            json={
                "object_id": object_id,
                "content_type_id": content_type_id,
                "title": title,
                "body": body,
                "icon_url": icon_url,
                "image_url": image_url,
                "redirect_url_web": redirect_url_web,
                "redirect_url_app": redirect_url_app,
                "topics": topics,
                "to_send": to_send,
                "scheduled_for": scheduled_for
            },
            timeout=_timeout
        )
        response.raise_for_status()
        return response

    @classmethod
    def update_notification(
        cls,
        id: int,
        object_id: str,
        content_type_id: str,
        title: str,
        body: str,
        icon_url: str,
        image_url: str,
        redirect_url_web: str,
        redirect_url_app: str,
        to_send: Optional[bool] = False,
        scheduled_for: Optional[datetime] = None, 
        topics: Optional[Iterable[str]] = None,
        api_key: Optional[str] = None,
        timeout: Optional[int] = None
    ) -> requests.Response:
        """Updates a given notification on communications

        :parameter id: Notification ID
        :parameter object_id: Object ID related to the notification in the application
        :parameter content_type_id: Content type ID related to the object associated to the notif.
        :parameter title: Notification title
        :parameter body: Notification body
        :parameter icon_url: Notification icon absolute URL
        :parameter image_url: Notification image absolute URL
        :parameter redirect_url_web: Redirect URL used in browser notifications
        :parameter redirect_url_app: Redirect URL used in application notifications
        :parameter to_send: True if the notification will be send after saved
        :parameter scheduled_for: Datetime that the notification will be send
        :parameter topics: Topics associated to the notification
        :parameter api_key: API Key, optional
        :parameter timeout: request timeout, optional
        :return: Response from communications
        :rtype: requests.Response
        """
        _api_key = api_key or cls.API_KEY
        _timeout = timeout or cls.TIMEOUT

        response = requests.put(
            settings.NOTIFICATION_API_URL.format(notification_id=id),
            headers=cls.__generate_headers(_api_key),
            json={
                "object_id": object_id,
                "content_type_id": content_type_id,
                "title": title,
                "body": body,
                "icon_url": icon_url,
                "image_url": image_url,
                "redirect_url_web": redirect_url_web,
                "redirect_url_app": redirect_url_app,
                "topics": topics,
                "to_send": to_send,
                "scheduled_for": scheduled_for
            },
            timeout=_timeout
        )
        response.raise_for_status()
        return response

    @classmethod
    def get_notification(
        cls,
        notification_id: int,
        api_key: Optional[str] = None,
        timeout: Optional[int] = None
    ) -> requests.Response:
        """Get a notification from communication by its ID

        :parameter notification_id: Notification ID that will be returned
        :parameter api_key: API Key, optional
        :parameter timeout: request timeout, optional
        :return: Response from communications
        :rtype: requests.Response
        """
        _api_key = api_key or cls.API_KEY
        _timeout = timeout or cls.TIMEOUT

        response = requests.get(
            settings.NOTIFICATION_API_URL.format(notification_id=notification_id),
            headers=cls.__generate_headers(_api_key),
            json={
                "notification_id": notification_id,
            },
            timeout=_timeout
        )
        response.raise_for_status()
        return response

    @classmethod
    def delete_notification(
        cls,
        id: int,
        api_key: Optional[str] = None,
        timeout: Optional[int] = None
    ) -> requests.Response:
        """Delete a notification from communications by its ID

        :parameter id: Notification ID that will be deleted
        :parameter api_key: API Key, optional
        :parameter timeout: request timeout, optional
        :return: Response from communications
        :rtype: requests.Response
        """
        _api_key = api_key or cls.API_KEY
        _timeout = timeout or cls.TIMEOUT

        response = requests.delete(
            settings.NOTIFICATION_API_URL.format(notification_id=id),
            headers=cls.__generate_headers(_api_key),
            json={},
            timeout=_timeout
        )
        response.raise_for_status()
        return response

    @classmethod
    def get_notification_datatable(
        cls,
        user_requester_email: str,
        post_data: dict,
        api_key: Optional[str] = None,
        timeout: Optional[int] = None
    ) -> requests.Response:
        """Get the notification datatable from communications

        :parameter user_requester_email: User that requests the datatable. # DEPRECATED
        :parameter post_data: request.POST data (Needed to simulate an internal request)
        :parameter api_key: API Key, optional
        :parameter timeout: request timeout, optional
        :return: Response from communications
        :rtype: requests.Response
        """
        _api_key = api_key or cls.API_KEY
        _timeout = timeout or cls.TIMEOUT

        response = requests.post(
            settings.GET_NOTIFICATION_LIST_API_URL,
            headers=cls.__generate_headers(_api_key),
            json={
                "user_requester_email": user_requester_email,
                "post_data": post_data
            },
            timeout=_timeout
        )
        response.raise_for_status()
        return response

    @classmethod
    def send_notification(
        cls,
        id: int,
        api_key: Optional[str] = None,
        timeout: Optional[int] = None
    ):
        """Send a notification by its ID

        :parameter id: Notification ID
        :parameter api_key: API Key, optional
        :parameter timeout: request timeout, optional
        :return: Response from communications
        :rtype: requests.Response
        """
        _api_key = api_key or cls.API_KEY
        _timeout = timeout or cls.TIMEOUT

        response = requests.post(
            settings.SEND_NOTIFICATION_API_URL.format(notification_id=id),
            headers=cls.__generate_headers(_api_key),
            timeout=_timeout
        )
        response.raise_for_status()
        return response

    @classmethod
    def create_topic(
        cls,
        name: str,
        slug: str,
        active: bool,
        object_id: Optional[int] = None,
        content_type_id: Optional[int] = None,
        api_key: Optional[str] = None,
        timeout: Optional[int] = None
    ) -> requests.Response:
        """Creates a new topic on communications system
        
        :parameter name: Topic name
        :parameter slug: Topic slug
        :parameter active: Is topic active?
        :parameter object_id: Topic object ID from source
        :parameter content_type_id: Topic content type ID from source
        :parameter api_key: API Key, optional
        :parameter timeout: request timeout, optional
        :return: Response from communications
        :rtype: requests.Response
        """
        _api_key = api_key or cls.API_KEY
        _timeout = timeout or cls.TIMEOUT

        response = requests.post(
            settings.CREATE_TOPIC_API_URL,
            headers=cls.__generate_headers(_api_key),
            json={
                "name": name,
                "slug": slug,
                "object_id": object_id,
                "content_type_id": content_type_id,
                "active": active,
            },
            timeout=_timeout
        )
        response.raise_for_status()
        return response

    @classmethod
    def update_topic(
        cls,
        id: int,
        name: str,
        slug: str,
        active: bool,
        object_id: Optional[int] = None,
        content_type_id: Optional[int] = None,
        api_key: Optional[str] = None,
        timeout: Optional[int] = None
    ) -> requests.Response:
        """Updates a topic in communications system using a given ID

        :parameter name: Topic name
        :parameter slug: Topic slug
        :parameter active: Is topic active?
        :parameter object_id: Topic object ID from source
        :parameter content_type_id: Topic content type ID from source
        :parameter api_key: API Key, optional
        :parameter timeout: request timeout, optional
        :return: Response from communications
        :rtype: requests.Response
        """
        _api_key = api_key or cls.API_KEY
        _timeout = timeout or cls.TIMEOUT

        response = requests.put(
            settings.TOPIC_API_URL.format(topic_identifier=id),
            headers=cls.__generate_headers(_api_key),
            json={
                "name": name,
                "slug": slug,
                "object_id": object_id,
                "content_type_id": content_type_id,
                "active": active,
            },
            timeout=_timeout
        )
        response.raise_for_status()
        return response

    @classmethod
    def delete_topic(
        cls,
        id: int,
        api_key: Optional[str] = None,
        timeout: Optional[int] = None
    ) -> requests.Response:
        """Delete a topic in communication and unsubscribe all devices from it

        :parameter id: Topic ID
        :parameter api_key: API Key, optional
        :parameter timeout: request timeout, optional
        :return: Response from communications
        :rtype: requests.Response
        """
        _api_key = api_key or cls.API_KEY
        _timeout = timeout or cls.TIMEOUT

        response = requests.delete(
            settings.TOPIC_API_URL.format(topic_identifier=id),
            headers=cls.__generate_headers(_api_key),
            timeout=_timeout
        )
        response.raise_for_status()
        return response

    @classmethod
    def get_topics_select2(
        cls,
        api_key: Optional[str] = None,
        timeout: Optional[int] = None
    ):
        """Get the topic select2 from communications. This will return all active topics that
        are not of type system and belongs to the actual application

        :parameter api_key: API Key, optional
        :parameter timeout: request timeout, optional
        :return: Response from communications
        :rtype: requests.Response
        """
        _api_key = api_key or cls.API_KEY
        _timeout = timeout or cls.TIMEOUT

        response = requests.get(
            settings.GET_TOPICS_SELECT2_API_URL,
            headers=cls.__generate_headers(_api_key),
            timeout=_timeout
        )
        response.raise_for_status()
        return response

    @classmethod
    def get_topic_datatable(
        cls,
        user_requester_email: str,
        post_data: dict,
        api_key: Optional[str] = None,
        timeout: Optional[int] = None
    ) -> requests.Response:
        """Get the topic datatable from communications

        :parameter user_requester_email: User that requests the datatable. # DEPRECATED
        :parameter post_data: request.POST data (Needed to simulate an internal request)
        :parameter api_key: API Key, optional
        :parameter timeout: request timeout, optional
        :return: Response from communications
        :rtype: requests.Response
        """
        _api_key = api_key or cls.API_KEY
        _timeout = timeout or cls.TIMEOUT

        response = requests.post(
            settings.GET_TOPIC_LIST_API_URL,
            headers=cls.__generate_headers(_api_key),
            json={
                "user_requester_email": user_requester_email,
                "post_data": post_data
            },
            timeout=_timeout
        )
        response.raise_for_status()
        return response

    @classmethod
    def get_topic(
        cls,
        topic_id: Optional[int] = None,
        topic_slug: Optional[str] = None,
        api_key: Optional[str] = None,
        timeout: Optional[int] = None
    ) -> Optional[requests.Response]:
        """Get a single topic by its ID or SLUG

        :parameter topic_id: Topic ID, optional but required if topic_slug is None
        :parameter topic_slug: Topic SLUG, optional but required if topic_id is None
        :parameter api_key: API Key, optional
        :parameter timeout: request timeout, optional
        :return: Response from communications, optional
        :rtype: requests.Response
        :raise: Exception if topic_id and topic_slug are not defined
        """
        _api_key = api_key or cls.API_KEY
        _timeout = timeout or cls.TIMEOUT

        if not topic_id and topic_slug:
            raise Exception()

        response = requests.get(
            settings.TOPIC_API_URL.format(topic_identifier=topic_id or topic_slug),
            headers=cls.__generate_headers(_api_key),
            timeout=_timeout
        )
        response.raise_for_status()
        return response
