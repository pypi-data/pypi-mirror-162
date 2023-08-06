import logging
import json
from typing import Optional

from django.shortcuts import redirect, render, reverse
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.utils.translation import gettext as _
from django.views.generic import View
from django.http import HttpResponse
from django.contrib import messages
from django.shortcuts import render
from django.conf import settings
import requests

from dnoticias_services.communications.forms import FCMNotificationForm, FCMTopicForm
from dnoticias_services.communications.notification import Notifications

logger = logging.getLogger(__name__)


class FCMNotificationListView(View):
    template_name = "backoffice/fcm-notifications/list.html"

    def get(self, request, *args, **kwargs):
        context = locals()
        context["table_id"] = "kt_datatable_fcm_notifications_search"
        context["notifications_search_field"] = 'kt_datatable_fcm_notifications_search_search'
        return render(request, self.template_name, context)


class FCMNotificationDatatableView(View):
    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        response = Notifications.get_notification_datatable(
            user_requester_email=request.user.email,
            post_data=json.dumps(request.POST.dict())
        )

        return HttpResponse(response)


class FCMNotificationFormView(View):
    template_name = "backoffice/fcm-notifications/form.html"

    def dispatch(self, request, *args, **kwargs):
        pk = kwargs.pop("pk", None)
        self.instance = None
        self.notification_data = {}

        if pk:
            self.notification_data = Notifications.get_notification(notification_id=pk).json()

        return super().dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        form = FCMNotificationForm(self.notification_data.get("data"))
        return render(request, self.template_name, locals())

    def post(self, request, *args, **kwargs):
        form = FCMNotificationForm(request.POST, request.FILES)
        was_successfull = False
        message = None

        if form.is_valid():
            was_successfull, message = form.save()

        return self.on_insucess(request, form, message) \
            if not was_successfull else \
                self.on_success(request, form, message)

    def add_success_message(self, request, message: Optional[str] = None):
        pass

    def add_insuccess_message(self, request, message: Optional[str] = None):
        pass

    def get_success_response(self, request, **context):
        return redirect(reverse("fcm-notification-list"))

    def get_insuccess_response(self, request, **context):
        return render(request, self.template_name, context)

    def on_success(self, request, form, message: Optional[str] = None):
        self.add_success_message(request, message)
        return self.get_success_response(request, form=form)

    def on_insucess(self, request, form, message: Optional[str] = None):
        self.add_insuccess_message(request, message)
        return self.get_insuccess_response(request, form=form)


class FCMNotificationCreateFormView(FCMNotificationFormView):
    def on_success(self, request, form, message: Optional[str] = None):
        return redirect(reverse("fcm-notification-list"))

    def add_success_message(self, request, message: Optional[str] = None):
        message = message or _("A notificação foi criada com sucesso.")
        messages.success(request, message, fail_silently=True)

    def add_insuccess_message(self, request, message: Optional[str] = None):
        message = message or _("Não foi possível criar a notificação.")
        messages.warning(request, message, fail_silently=True)


class FCMNotificationUpdateFormView(FCMNotificationFormView):
    def add_success_message(self, request, message: Optional[str] = None):
        message = message or _("A notificação foi atualizada com sucesso.")
        messages.success(request, message, fail_silently=True)

    def add_insuccess_message(self, request, message: Optional[str] = None):
        message = message or _("Não foi possível atualizar a notificação.")
        messages.warning(request, message, fail_silently=True)


class FCMNotificationDeleteView(View):
    def post(self, request, *args, **kwargs):
        try:
            Notifications.delete_notification(id=kwargs.get("pk"))
        except requests.exceptions.HTTPError:
            logger.exception("Cannot delete notification")
            messages.error(request, "Ocorreu um erro ao tentar eliminar a notificação")

        return redirect(reverse("fcm-notification-list"))

    def add_message(self, request):
        messages.info(request, _("A notificação foi eliminada."), fail_silently=True)


class FCMNotificationSendView(View):
    def post(self, request, *args, **kwargs):
        try:
            Notifications.send_notification(
                kwargs.get("pk"),
                settings.NOTIFICATIONS_APPLICATION_DOMAIN
            )
        except requests.exceptions.HTTPError as e:
            logger.exception("Cannot send notification")
            messages.error(request, "Ocorreu um erro ao tentar enviar a notificação")

        return redirect(reverse("fcm-notification-list"))


class FCMTopicsListView(View):
    template_name = "backoffice/fcm-topics/list.html"

    def get(self, request, *args, **kwargs):
        context = locals()
        context["table_id"] = "kt_datatable_fcm_topics_search"
        context["table_search_id"] = 'kt_datatable_fcm_topics_search_search'
        return render(request, self.template_name, context)


class FCMTopicsDatatableView(View):
    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        response = Notifications.get_topic_datatable(
            user_requester_email=request.user.email,
            post_data=json.dumps(request.POST.dict())
        )

        return HttpResponse(response)


class FCMTopicFormView(View):
    template_name = "backoffice/fcm-topics/form.html"

    def dispatch(self, request, *args, **kwargs):
        pk = kwargs.pop("pk", None)
        self.topic_data = {}

        if pk:
            self.topic_data = Notifications.get_topic(topic_id=pk).json()
            print("HAS PK!")

        return super().dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        form = FCMTopicForm(self.topic_data.get("data"))
        return render(request, self.template_name, locals())

    def post(self, request, *args, **kwargs):
        form = FCMTopicForm(request.POST, request.FILES)
        was_successfull = False
        message = None

        if form.is_valid():
            was_successfull, message = form.save()

        return self.on_insucess(request, form, message) \
            if not was_successfull else \
                self.on_success(request, form, message)

    def add_success_message(self, request, message: Optional[str] = None):
        pass

    def add_insuccess_message(self, request, message: Optional[str] = None):
        pass

    def get_success_response(self, request):
        return redirect(reverse("fcm-topic-list"))

    def get_insuccess_response(self, request, **context):
        return render(request, self.template_name, context)

    def on_success(self, request, form, message: Optional[str] = None):
        self.add_success_message(request, message)
        return self.get_success_response(request)

    def on_insucess(self, request, form, message: Optional[str] = None):
        self.add_insuccess_message(request, message)
        return self.get_insuccess_response(request, form=form)


class FCMTopicsCreateView(FCMTopicFormView):
    def add_success_message(self, request, message: Optional[str] = None):
        message = message or _("O tópico foi criado com sucesso.")
        messages.success(request, message, fail_silently=True)

    def add_insuccess_message(self, request, message: Optional[str] = None):
        message = message or _("Não foi possível criar o tópico.")
        messages.warning(request, message, fail_silently=True)


class FCMTopicsUpdateView(FCMTopicFormView):
    def add_success_message(self, request, message: Optional[str] = None):
        message = message or _("O tópico foi atualizado com sucesso.")
        messages.success(request, message, fail_silently=True)

    def add_insuccess_message(self, request, message: Optional[str] = None):
        message = message or _("Não foi possível atualizar o tópico.")
        messages.warning(request, message, fail_silently=True)


class FCMTopicDeleteView(View):
    def post(self, request, *args, **kwargs):
        try:
            Notifications.delete_topic(id=kwargs.get("pk"))
        except requests.exceptions.HTTPError:
            logger.exception("Cannot delete notification")
            messages.error(request, "Ocorreu um erro ao tentar eliminar o tópico")
        else:
            messages.info(request, _("O tópico foi eliminado."), fail_silently=True)

        return redirect(reverse("fcm-topic-list"))


class FCMTopicSelect2View(View):
    def get(self, request, *args, **kwargs):
        return Notifications.get_topics_select2()
