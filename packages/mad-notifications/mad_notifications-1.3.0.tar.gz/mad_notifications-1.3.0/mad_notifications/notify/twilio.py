from celery import shared_task
import logging
from mad_notifications.models import get_notification_model
from mad_notifications.senders.twilio import sendTwilioSMSNotification, sendTwilioWhatsAppNotification

logger = logging.getLogger(__name__)


# Tasks to send respective notifications

@shared_task(name="Non-Periodic: Twilio SMS notification")
def twilio_SMS_notification(notification_id):
    try:
        notification_obj = get_notification_model().objects.get(id=notification_id)
        
        sendTwilioSMSNotification(notification_obj)
        return "SMS notifications sent"
        

    except Exception as e:
        logger.error(str(e))
        return "Unable to send Email notification: " + str(e)



@shared_task(name="Non-Periodic: Twilio WhatsApp notification")
def twilio_WhatsApp_notification(notification_id):
    try:
        notification_obj = get_notification_model().objects.get(id=notification_id)
        
        sendTwilioWhatsAppNotification(notification_obj)
        return "WhatsApp notifications sent"
        

    except Exception as e:
        logger.error(str(e))
        return "Unable to send Email notification: " + str(e)
