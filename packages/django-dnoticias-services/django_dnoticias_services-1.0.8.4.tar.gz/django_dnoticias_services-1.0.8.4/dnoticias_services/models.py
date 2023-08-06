from django.db import models


class CommunicationPermissions(models.Model):
    class Meta:
        managed = False
        default_permissions = ()
        permissions = (
            ("view_notifications", "View notifications"),
            ("add_notifications", "Add notifications"),
            ("change_notifications", "Edit notifications"),
            ("delete_notifications", "Delete notifications"),
            ("view_topics", "View topics"),
            ("add_topics", "Add topics"),
            ("change_topics", "Edit topics"),
            ("delete_topics", "Delete topics"),
        )
