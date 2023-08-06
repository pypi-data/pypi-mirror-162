from mad_notifications.utils import notificaion_unique_file_path
from django.db import models
from django.contrib.auth import get_user_model
from django.apps import apps
from mad_notifications.settings import notification_settings


# Create your models here.

class UserNotificationConfigAbstract(models.Model):
    """
    Depending on the provider settings, determine if the notification should be sent or not.
    """
    user = models.ForeignKey(get_user_model(), unique=True, primary_key=True, on_delete=models.CASCADE)
    allow_email = models.BooleanField(default=True, help_text="")
    allow_push = models.BooleanField(default=True, help_text="")
    allow_sms = models.BooleanField(default=True, help_text="")
    allow_whatsapp = models.BooleanField(default=True, help_text="")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class UserNotificationConfig(UserNotificationConfigAbstract):
    pass
# ================================================================================================================================================

class EmailTemplateAbstract(models.Model):
    id = models.BigAutoField(unique=True, primary_key=True)
    name = models.CharField(max_length=225, blank=False, null=False, help_text="Template Name")
    slug = models.SlugField(max_length=225, blank=False, null=False, unique=True, help_text="Unique Template identifier")
    subject = models.CharField(max_length=225, default="Email Subject here", blank=False, null=False, help_text="Email Subject")
    content = models.TextField(blank=False, null=False, help_text='Templated content of the email. <a href="https://docs.djangoproject.com/en/dev/topics/templates/" target="_target">Refer to docs for more details</a>. Supports HTML')
    from_email = models.CharField(max_length=225, blank=True, null=True, help_text='For example: No Reply &lt;noreply@example.com&gt;')
    admin_note = models.TextField(blank=True, null=True, help_text="")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


    class Meta:
        abstract = True
        ordering = ['-id']

    def __str__(self):
        return str(self.name) + " - " + str(self.slug)


class EmailTemplate(EmailTemplateAbstract):
    pass


# ================================================================================================================================================
class DeviceAbstract(models.Model):
    id = models.BigAutoField(unique=True, primary_key=True)
    user = models.ForeignKey(get_user_model(), on_delete=models.SET_NULL, blank=False, null=True)
    token = models.TextField(blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True
        ordering = ['-id']


class Device(DeviceAbstract):
    pass

# ================================================================================================================================================

class NotificationAbstract(models.Model):
    id = models.BigAutoField(unique=True, primary_key=True)
    user = models.ForeignKey(get_user_model(), on_delete=models.SET_NULL, blank=False, null=True)
    title = models.CharField(max_length=254, blank=False, null=False)
    content = models.TextField(blank=False, null=True)
    image = models.FileField(upload_to=notificaion_unique_file_path, blank=True, null=True)
    icon = models.FileField(upload_to=notificaion_unique_file_path, blank=True, null=True)
    is_read = models.BooleanField(default=False)
    actions = models.JSONField(default=dict, blank=True, help_text="")
    data = models.JSONField(default=dict, blank=True, help_text="All keys and values in the dictionary must be strings.")
    template = models.ForeignKey(EmailTemplate, blank=True, null=True, on_delete=models.SET_NULL)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


    class Meta:
        abstract = True
        ordering = ['-id']



class Notification(NotificationAbstract):
    pass


# ================================================================================================================================================


# Model methods

def get_user_notification_config_model():
    """Return the Notification model that is active in this project."""
    return apps.get_model(notification_settings.USER_NOTIFICATION_CONFIG_MODEL)

def get_notification_model():
    """Return the Notification model that is active in this project."""
    return apps.get_model(notification_settings.NOTIFICATION_MODEL)


def get_email_template_model():
    """Return the Notification model that is active in this project."""
    return apps.get_model(notification_settings.EMAIL_TEMPLATE_MODEL)


def get_device_model():
    """Return the Notification model that is active in this project."""
    return apps.get_model(notification_settings.DEVICE_MODEL)