from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class NotificationsConfig(AppConfig):
    name = 'mad_notifications'
    verbose_name = 'Notifications'

    def ready(self):
        import mad_notifications.signals