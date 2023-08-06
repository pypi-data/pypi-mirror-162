import logging
import firebase_admin
from mad_notifications.models import get_notification_model
from celery import shared_task

from mad_notifications.senders.firebase import sendFirebaseMobilePushNotification

# Get an instance of a logger
logger = logging.getLogger(__name__)

"""
https://firebase.google.com/docs/cloud-messaging/auth-server#use-credentials-to-mint-access-tokens
https://github.com/firebase/firebase-admin-python/blob/e35a45a68885d1edfe7a28a2e75a9f1cc444f272/snippets/messaging/cloud_messaging.py
"""

FIREBASE_APP = firebase_admin.initialize_app()
SCOPES = [
        'https://www.googleapis.com/auth/firebase.messaging'
    ]

def get_access_token():
        """
        Retrieve a valid access token that can be used to authorize requests.
        :return: Access token.
        """
        access_token_info = FIREBASE_APP.get_access_token()
        return access_token_info.access_token


@shared_task(name="Non-Periodic: Push notification")
def push_notification(notification_id):
    notification_obj = get_notification_model().objects.get(id=notification_id)
    # context = json.loads(notification_obj.notification_context)
    devices = notification_obj.user.device_set.all()
    if notification_obj.content is not None:
        for device in devices:
            try:
                sendFirebaseMobilePushNotification(device, notification_obj)
                logger.info("Push notifiaction sent to device: " + str(device.id))
            except Exception as e:
                logger.error( "Could not send push notification to device: " + str(device.id) + " message: " + str(e) )

        return "Push notifications sent"
    else:
        return "Error Notification has not content"
