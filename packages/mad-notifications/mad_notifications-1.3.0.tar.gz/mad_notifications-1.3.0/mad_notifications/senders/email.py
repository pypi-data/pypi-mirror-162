import datetime
from django.conf import settings
from mad_notifications.settings import notification_settings
from django.template import Template, Context
from django.core.mail import send_mail
from django.conf import settings
import logging

from mad_notifications.user import NotificationConfig

logger = logging.getLogger(__name__)

class EmailNotification(NotificationConfig):
    
    def __init__(self, notification):
        self.notification = notification


    def emailNotification(self):
        notification_obj = self.notification

        # from email
        try:
            if notification_obj.template.from_email is not None or notification_obj.template.from_email != "":
                from_email = notification_obj.template.from_email
        except Exception as e:
            logger.error(str(e))
            from_email = settings.DEFAULT_FROM_EMAIL
        
        try:
            if notification_obj.template.subject is not None or notification_obj.template.subject != "":
                subject_template = Template(notification_obj.template.subject)
                subject_context = Context(notification_obj.data)
                subject = subject_template.render(subject_context)
            else:
                subject = notification_obj.title
        except Exception as e:
            logger.error(str(e))
            subject = notification_obj.title

        # templating of email content
        try:
            template = Template(notification_obj.template.content)
            context = Context(notification_obj.data)
            html_message = template.render(context)
        except Exception as e:
            logger.error(str(e))
            html_message = None


        # send email
        try:
            sent = send_mail(
                subject = subject,
                message = notification_obj.content,
                from_email = from_email,
                recipient_list = [notification_obj.user.email],
                fail_silently = False,
                html_message = html_message,
            )
            return sent
        except Exception as e:
            raise



def sendEmailNotification(notification):
    email_notification = notification_settings.EMAIL_NOTIFICATION_CLASS(notification)
    return email_notification.emailNotification()