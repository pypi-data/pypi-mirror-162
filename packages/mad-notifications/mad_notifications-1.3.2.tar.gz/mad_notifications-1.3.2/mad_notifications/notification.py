from mad_notifications.models import get_notification_model

import logging
logger = logging.getLogger(__name__)

class Notification:
    def __init__(self, **kwargs):
        self.__dict__.update(**kwargs)
        self.notification_obj = kwargs

    def notify(self, fail_silently=False):
        try:
            return get_notification_model().objects.create(**self.notification_obj)
        except Exception as e:
            logger.warning(str(e))
            if fail_silently is True:
                return None
            else:
                raise
