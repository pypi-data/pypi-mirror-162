# Mad Notifications

Mad Notifications app for django to send notifications to the user

## Quick start

1. Add "mad_notifications" to your INSTALLED_APPS setting like this:

    ```python
    INSTALLED_APPS = [
        ...
        'mad_notifications',
    ]
    ```

2. Include the notifications URLconf in your project urls.py like this:

    ```python
    path('notifications/', include('mad_notifications.api.urls')),
    ```

3. Run `python manage.py migrate` to create the polls models.

## Usage

```python
from mad_notifications.notification import Notification
# create a notification
notification = Notification(
    user = user,
    title = "New Order",
    content = "You have a new order!",
    data = {
        'order': order_data,
    },
    actions = {
        'click_action': "ORDER_SCREEN"
    }
)
# send the notification
notification.notify()
```

## Overriding default

```python
MAD_NOTIFICATIONS = {
    "FIREBASE_MOBILE_PUSH_NOTIFICATION_CLASS": "mad_notifications.senders.firebase.FirebaseMobilePushNotification",
    "EMAIL_NOTIFICATION_CLASS": "mad_notifications.senders.email.EmailNotification",
}
```

## Developer Guide

### Setting up a new provider

Create logic in `~/sendenrs/PROVIDER.py` and call via tasks in `~/notify/PROVIDER.py`
