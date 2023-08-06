

from django.db.models.signals import post_save
from django.dispatch import receiver
from mad_notifications.notify.email import email_notification
from mad_notifications.notify.firebase import push_notification
from mad_notifications.models import get_notification_model
from mad_notifications.notify.twilio import twilio_SMS_notification


@receiver(post_save, sender=get_notification_model())
def NotificationPostSave(sender, instance, created, update_fields, **kwargs):
    if created:
        # send the notification
        push_notification.apply_async(
            [instance.id],
            countdown=1
        )

        email_notification.apply_async(
            [instance.id],
            countdown=1
        )
        
        twilio_SMS_notification.apply_async(
            [instance.id],
            countdown=1
        )
