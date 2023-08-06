from notifications import views
from django.urls import path

from . import views


urlpatterns = [
    path("list/", views.FCMNotificationListView.as_view(), name="fcm-notification-list"),
    path("datatable/", views.FCMNotificationDatatableView.as_view(), name="fcm-notification-datatable"),
    path("create/", views.FCMNotificationCreateFormView.as_view(), name="fcm-notification-create"),
    path("<int:pk>/", views.FCMNotificationUpdateFormView.as_view(), name="fcm-notification-update"),
    path("delete/<int:pk>/", views.FCMNotificationDeleteView.as_view(), name="fcm-notification-delete"),
    path("send/<int:pk>/", views.FCMNotificationSendView.as_view(), name="fcm-notification-send"),

    path("topic-select2-view/", views.FCMTopicSelect2View.as_view(), name="fcm-topic-select2"),

    path("topics/", views.FCMTopicsListView.as_view(), name="fcm-topic-list"),
    path("topics/datatable/", views.FCMTopicsDatatableView.as_view(), name="fcm-topic-datatable"),
    path("topics/create/", views.FCMTopicsCreateView.as_view(), name="fcm-topic-create"),
    path("topics/<int:pk>/", views.FCMTopicsUpdateView.as_view(), name="fcm-topic-update"),
    path("topics/delete/<int:pk>/", views.FCMTopicDeleteView.as_view(), name="fcm-topic-delete"),
]