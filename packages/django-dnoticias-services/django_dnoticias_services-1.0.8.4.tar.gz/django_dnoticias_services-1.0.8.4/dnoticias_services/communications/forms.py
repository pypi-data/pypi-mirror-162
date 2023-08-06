import logging
import json
from urllib.parse import urlparse

from django.contrib.contenttypes.models import ContentType
from django.utils.translation import gettext_lazy as _
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from django.conf import settings
from django import forms

import requests
from dnoticias_services.communications.notification import Notifications

logger = logging.getLogger(__name__)


class BaseFCMTopicForm(forms.Form):
    def setup_topics(self):
        topics_choices = self.get_topics_choices()
        self.fields["topics"].choices = topics_choices

    def get_topics_choices(self):
        try:
            response = Notifications.get_topics_select2()
            context = response.json()

            choices = []
            for element in context.get("results", []):
                for el in element.get("children", []):
                    choices.append(
                        [el["id"], el["text"]]
                    )

            return choices
        except Exception as e:
            logger.exception("Error in thetting the topics choices.")
            return []


class FCMNotificationForm(BaseFCMTopicForm):
    id = forms.IntegerField(widget=forms.HiddenInput(), required=False)
    object_id = forms.IntegerField(widget=forms.HiddenInput(), required=False)
    content_type_id = forms.IntegerField(widget=forms.HiddenInput(), required=False)
    icon = forms.ImageField(required=False, widget=forms.FileInput(), label=_("Icon"))
    title = forms.CharField(label=_("Titulo"))
    body = forms.CharField(label=_("Corpo"), required=False)
    is_scheduled = forms.BooleanField(label=_("Agendar"), required=False)
    scheduled_for = forms.CharField(label=_("Data de agendamento"), required=False)
    redirect_url_web = forms.CharField(label=_("Hiperligação para o formato Website"))
    redirect_url_app = forms.CharField(label=_("Hiperligação para o formato Aplicação"))
    topics = forms.MultipleChoiceField(choices=[], label=_("Tópicos"))
    scrap_url = forms.URLField(
        required=False,
        label=_("Hiperligação para retirar dados")
    )
    image = forms.ImageField(required=False, widget=forms.FileInput(), label=_("Imagem"))
    image_url = forms.URLField(required=False, widget=forms.HiddenInput())
    icon_url = forms.URLField(
        required=False,
        widget=forms.HiddenInput(),
        initial=getattr(settings, "NOTIFICATIONS_DEFAULT_ICON", "")
    )
    to_send = forms.BooleanField(required=False, initial=False, label=_("Enviar"))

    class Meta:
        widgets = {
            "activate_date": forms.HiddenInput(),
            "body": forms.Textarea(attrs={'cols': '40', 'rows': '5'}),
        }

    def __init__(self, notification_data, files=None, **kwargs):
        super().__init__(notification_data, files, **kwargs)
        self.setup_topics()

        if notification_data:
            self.fields["is_scheduled"].initial = bool(notification_data.get("scheduled_for", False))

            if notification_data.get("sent"):

                for field in self.fields:
                    self.fields[field].widget.attrs['disabled'] = True

                del self.fields["to_send"]
                del self.fields["scrap_url"]
        else:
            self.fields["icon"].initial = default_storage.url("/files/siteconfig/icon/icon_notif.png")

        self.default_icon = self.get_remote_content(
            getattr(settings, "NOTIFICATIONS_DEFAULT_ICON", "")
        )

    def get_redirect_url_output_field_name(self, output) -> str:
        return "redirect_url_{}".format(output)

    def _save_file_get_path(self, file_name, file_bytes) -> str:
        file = default_storage.save(
            file_name,
            ContentFile(file_bytes)
        )
        return default_storage.url(file)

    def clean(self):
        cleaned_data = super().clean()

        icon_url = cleaned_data.get("icon_url")
        image_url = cleaned_data.get("image_url")

        if icon_url:
            cleaned_data["external_icon"] = self.get_remote_content(icon_url)

        if image_url:
            cleaned_data["external_image"] = self.get_remote_content(image_url)

    def get_remote_content(self, url) -> str:
        response = requests.get(url)

        if response.status_code == 200:
            return response.content
        else:
            return ""

    def get_article_id_from_url(self) -> str:
        redirect_url_web: str = self.cleaned_data.get("redirect_url_web")
        article_slug = redirect_url_web.split("/")[6]
        article_id = article_slug.split("-")[0]
        return article_id

    def get_image_path(self, filename: str) -> str:
        return f"/notifications/images/{filename}"

    def get_icon_path(self, filename: str) -> str:
        return f"/notifications/icon/{filename}"

    def save(self, commit=True):
        self.ready_output_options = ["app", "web"]
        content_type_id = ContentType.objects.get(app_label="news", model="article").id
        object_id = self.get_article_id_from_url()
        data = {
            "object_id": object_id,
            "content_type_id": content_type_id,
            "title": self.cleaned_data.get("title", ""),
            "icon_url": "",
            "image_url": "",
            "body": self.cleaned_data.get("body", ""),
            "redirect_url_web": "",
            "redirect_url_app": "",
            "topics": json.dumps(self.cleaned_data.get("topics")),
            "scheduled_for": "",
            "to_send": self.cleaned_data.get("to_send", False)
        }

        notification_id = self.cleaned_data.get("id")

        if notification_id:
            data.update({"id": notification_id})

        for output in self.ready_output_options:
            output_redirect_field_name = self.get_redirect_url_output_field_name(output)
            data[f"redirect_url_{output}"] = self.cleaned_data[output_redirect_field_name]

        image = self.cleaned_data.get("image")
        external_image = self.cleaned_data.get("image_url")

        if image:
            data["image_url"] = self._save_file_get_path(
                self.get_image_path(image._name),
                image.read()
            )
        elif external_image:
            data["image_url"] = self._save_file_get_path(
                self.get_image_path("notification_image.jpeg"),
                self.get_remote_content(external_image)
            )

        icon = self.cleaned_data.get("icon")
        external_icon = self.cleaned_data.get("icon_url")

        if icon:
            data["icon_url"] = self._save_file_get_path(
                self.get_icon_path(icon._name),
                icon.read()
            )
        elif external_icon:
            data["icon_url"] = self._save_file_get_path(
                self.get_icon_path("notification_icon.jpeg"),
                self.get_remote_content(external_icon)
            )
        else:
            data["icon_url"] = self._save_file_get_path(
                self.get_icon_path("notification_icon.jpeg"),
                self.default_icon
            )

        if self.cleaned_data["is_scheduled"]:
            data["scheduled_for"] = self.cleaned_data["scheduled_for"]

        try:
            if notification_id:
                Notifications.update_notification(**data)
            else:
                Notifications.create_notification(**data)
        except requests.exceptions.HTTPError as e:
            logger.exception("Cannot create/update notification in communications")

            if e.response.status_code != 500:
                return False, e.response.json().get("error")
            else:
                return False, None

        return True, None


class FCMTopicForm(forms.Form):
    id = forms.IntegerField(widget=forms.HiddenInput(), required=False)
    object_id = forms.IntegerField(widget=forms.HiddenInput(), required=False)
    content_type_id = forms.IntegerField(widget=forms.HiddenInput(), required=False)
    name = forms.CharField(label=_("Nome"))
    slug = forms.SlugField(label=_("Slug"))
    active = forms.BooleanField(label=_("Ativo"), required=False)

    def __init__(self, topic_data, files=None, **kwargs):
        super().__init__(topic_data, files, **kwargs)
        self.is_system = False

        if topic_data:
            self.id = topic_data.get("id")
            if topic_data.get("is_system"):
                self.is_system = topic_data.get("is_system")
                for field in self.fields:
                    self.fields[field].widget.attrs['disabled'] = True

    def save(self, commit=True):
        if commit:
            data = {
                "name": self.cleaned_data.get("name"),
                "slug": self.cleaned_data.get("slug"),
                "active": self.cleaned_data.get("active", False)
            }

            if self.id:
                data.update({"id": self.id})

            try:
                if self.id:
                    Notifications.update_topic(**data)
                else:
                    Notifications.create_topic(**data)
            except requests.exceptions.HTTPError as e:
                if e.response.status_code != 500:
                    logger.exception("Cannot create/update topic")
                    return False, e.response.json().get("error")
                else:
                    return False, None

            return True, None
