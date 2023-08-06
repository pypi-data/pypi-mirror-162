from django.conf import settings
from django.utils.module_loading import import_string
from django.core.exceptions import ImproperlyConfigured
from django.test.signals import setting_changed

USER_SETTINGS = getattr(settings, "MAD_NOTIFICATIONS", None)


USER_NOTIFICATION_CONFIG_MODEL = "mad_notifications.UserNotificationConfig"

NOTIFICATION_MODEL = getattr(settings, "MAD_NOTIFICATIONS_NOTIFICATION_MODEL", "mad_notifications.Notification")
EMAIL_TEMPLATE_MODEL = getattr(settings, "MAD_NOTIFICATIONS_EMAIL_TEMPLATE_MODEL", "mad_notifications.EmailTemplate")
DEVICE_MODEL = getattr(settings, "MAD_NOTIFICATIONS_DEVICE_MODEL", "mad_notifications.Device")

TWILIO_ACCOUNT_SID = getattr(settings, "TWILIO_ACCOUNT_SID", None)
TWILIO_ACCOUNT_AUTH_TOKEN = getattr(settings, "TWILIO_ACCOUNT_AUTH_TOKEN", None)
TWILIO_ACCOUNT_PHONE_NUMBER = getattr(settings, "TWILIO_ACCOUNT_PHONE_NUMBER", None)


DEFAULTS = {
    "NOTIFICATION_MODEL": NOTIFICATION_MODEL,
    "EMAIL_TEMPLATE_MODEL": EMAIL_TEMPLATE_MODEL,
    "DEVICE_MODEL": DEVICE_MODEL,
    'USER_NOTIFICATION_CONFIG_MODEL': USER_NOTIFICATION_CONFIG_MODEL,

    # Firebase Defaults
    "FIREBASE_MOBILE_PUSH_NOTIFICATION_CLASS": "mad_notifications.senders.firebase.FirebaseMobilePushNotification",

    # Email Defaults
    "EMAIL_NOTIFICATION_CLASS": "mad_notifications.senders.email.EmailNotification",

    # Twillio Defaults
    "TWILIO_NOTIFICATION_CLASS": "mad_notifications.senders.twilio.TwilioNotification",
    'TWILIO_ACCOUNT_SID': TWILIO_ACCOUNT_SID,
    'TWILIO_ACCOUNT_AUTH_TOKEN': TWILIO_ACCOUNT_AUTH_TOKEN,
    'TWILIO_ACCOUNT_PHONE_NUMBER': TWILIO_ACCOUNT_PHONE_NUMBER

    # Add more as required.
}

IMPORT_STRINGS = (
    "FIREBASE_MOBILE_PUSH_NOTIFICATION_CLASS",
    "EMAIL_NOTIFICATION_CLASS",
    'TWILIO_NOTIFICATION_CLASS',
)

MANDATORY = IMPORT_STRINGS


def perform_import(val, setting_name):
    """
    If the given setting is a string import notation,
    then perform the necessary import or imports.
    """
    if val is None:
        return None
    elif isinstance(val, str):
        return import_from_string(val, setting_name)
    elif isinstance(val, (list, tuple)):
        return [import_from_string(item, setting_name) for item in val]
    return val


def import_from_string(val, setting_name):
    """
    Attempt to import a class from a string representation.
    """
    try:
        return import_string(val)
    except ImportError as e:
        msg = "Could not import %r for setting %r. %s: %s." % (val, setting_name, e.__class__.__name__, e)
        raise ImportError(msg)



class MadNotificationSettings:

    def __init__(self, user_settings=None, defaults=None, import_strings=None, mandatory=None):
        self._user_settings = user_settings or {}
        self.defaults = defaults or DEFAULTS
        self.import_strings = import_strings or IMPORT_STRINGS
        self.mandatory = mandatory or ()
        self._cached_attrs = set()


    @property
    def user_settings(self):
        if not hasattr(self, "_user_settings"):
            self._user_settings = getattr(settings, "MAD_NOTIFICATIONS", {})
        return self._user_settings


    def __getattr__(self, attr):
        if attr not in self.defaults:
            raise AttributeError("Invalid Mad Notifications setting: %s" % attr)

        try:
            # Check if present in user settings
            val = self.user_settings[attr]
        except KeyError:
            val = self.defaults[attr]

        if val and attr in self.import_strings:
            val = perform_import(val, attr)

        self.validate_setting(attr, val)
        self._cached_attrs.add(attr)
        setattr(self, attr, val)
        return val


    def validate_setting(self, attr, val):
        if not val and attr in self.mandatory:
            raise AttributeError("mad_notifications setting: %s is mandatory" % attr)

    def reload(self):
        for attr in self._cached_attrs:
            delattr(self, attr)
        self._cached_attrs.clear()
        if hasattr(self, "_user_settings"):
            delattr(self, "_user_settings")

notification_settings = MadNotificationSettings(USER_SETTINGS, DEFAULTS, IMPORT_STRINGS, MANDATORY)


def reload_mad_notification_settings(*args, **kwargs):
    setting = kwargs["setting"]
    if setting == "MAD_NOTIFICATIONS":
        notification_settings.reload()

setting_changed.connect(reload_mad_notification_settings)