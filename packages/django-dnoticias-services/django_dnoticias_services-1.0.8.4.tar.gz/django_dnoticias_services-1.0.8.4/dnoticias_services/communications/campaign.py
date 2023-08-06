from typing import Optional

from django.conf import settings

import requests

from dnoticias_services.communications.base import BaseMailRequest
from dnoticias_services.utils.request import get_headers


class BaseCampaign(BaseMailRequest):
    def __call__(
        self,
        template_uuid: str,
        brand_group_uuid: str,
        newsletter_uuid: str,
        title: str,
        subject: str,
        context: Optional[dict] = dict(),
        from_email: Optional[str] = None,
        from_name: Optional[str] = None,
        track_opens: Optional[bool] = True,
        track_clicks: Optional[bool] = True,
        internal: Optional[bool] = False,
        api_key: Optional[str] = None,
        timeout: Optional[int] = None
    ):
        url = self.get_url()
        _api_key = api_key or self.api_key
        _timeout = timeout or self.timeout

        response = requests.post(
            url,
            headers=get_headers(_api_key),
            json={
                "template_uuid": template_uuid,
                "brand_group_uuid": brand_group_uuid,
                "newsletter_uuid": newsletter_uuid,
                "title": title,
                "subject": subject,
                "context": context,
                "from_email": from_email,
                "from_name": from_name,
                "track_opens": track_opens,
                "track_clicks": track_clicks,
                "internal": internal,
            },
            timeout=_timeout
        )
        response.raise_for_status()
        return response

    def get_url(self):
        return None


class SendCampaign(BaseCampaign):
    def get_url(self):
        return settings.SEND_CAMPAIGN_API_URL


class CreateCampaign(BaseCampaign):
    def get_url(self):
        return settings.CREATE_CAMPAIGN_API_URL


send_campaign = SendCampaign()
create_campaign = CreateCampaign()


__all__ = ("send_campaign", "create_campaign")
