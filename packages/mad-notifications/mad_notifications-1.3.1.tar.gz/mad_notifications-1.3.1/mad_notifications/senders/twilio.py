import datetime
from django.conf import settings
from mad_notifications.settings import notification_settings
from django.template import Template, Context
from twilio.rest import Client
from django.conf import settings
import logging

logger = logging.getLogger(__name__)

class TwilioNotification:
    
    def __init__(self, notification):
        self.notification = notification
        self.TWILIO_ACCOUNT_SID = notification_settings.TWILIO_ACCOUNT_SID
        self.TWILIO_ACCOUNT_AUTH_TOKEN = notification_settings.TWILIO_ACCOUNT_AUTH_TOKEN
        self.TWILIO_ACCOUNT_PHONE_NUMBER = notification_settings.TWILIO_ACCOUNT_PHONE_NUMBER
        
        self.twilioClient = Client(self.TWILIO_ACCOUNT_SID, self.TWILIO_ACCOUNT_AUTH_TOKEN)
        


    def smsNotification(self):
        notification_obj = self.notification
        # send SMS
        try:
            message = self.twilioClient.messages.create(
                body = notification_obj.content,
                from_ = str(self.TWILIO_ACCOUNT_PHONE_NUMBER),
                to = str(notification_obj.user.phone)
            )
            return message
        
        except Exception as e:
            logger.error(str(e))
            raise
    
    
    def WhatsAppNotification(self):
        notification_obj = self.notification
        # send SMS
        try:
            message = self.twilioClient.messages.create(
                body = notification_obj.content,
                from_ = 'whatsapp:' + str(self.TWILIO_ACCOUNT_PHONE_NUMBER),
                to = 'whatsapp:' + str(notification_obj.user.phone)
            )
            return message
        
        except Exception as e:
            logger.error(str(e))
            raise



def sendTwilioSMSNotification(notification):
    twilio_notification = notification_settings.TWILIO_NOTIFICATION_CLASS(notification)
    return twilio_notification.smsNotification()


def sendTwilioWhatsAppNotification(notification):
    twilio_notification = notification_settings.TWILIO_NOTIFICATION_CLASS(notification)
    return twilio_notification.WhatsAppNotification()