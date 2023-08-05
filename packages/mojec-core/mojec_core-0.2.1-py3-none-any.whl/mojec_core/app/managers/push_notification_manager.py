from typing import Optional

from onesignal_sdk.client import Client
from onesignal_sdk.error import OneSignalHTTPError

from mojec_core import settings
from mojec_core.utils import log_exception


class PushNotificationManager:
    client = Client(app_id=settings.ONE_SIGNAL_APP_ID,
                    rest_api_key=settings.ONE_SIGNAL_REST_API_KEY,
                    user_auth_key=settings.ONE_SIGNAL_USER_AUTH_KEY)

    def send(self, msg, data=None, uid=None, user: Optional = None):
        from mojec_core.app.models import User
        """
        For sending push notification to all user devices
        by passing either uid or user object

        :param msg: The text to be sent as notification content
        :param data: data to be sent along with the notification
        :param uid: can be user.id or user.uid.
        :param user:
        :return:
        """
        try:
            if uid:
                if '-' in uid:
                    user = User.objects.get(uid=uid)
                else:
                    user = User.objects.get(id=uid)
            include_player_ids = user.fcmToken
            if bool(include_player_ids):
                notification_body = {
                    'contents': {'en': msg},
                    'data': data,
                    'include_player_ids': include_player_ids
                }

                # Make a request to OneSignal and parse response
                response = self.client.send_notification(notification_body)
                print("---------PushNotificationManager-------------")
                print(response.body)  # JSON parsed response
                print("---------/PushNotificationManager/-------------")

        except OneSignalHTTPError as e:  # An exception is raised if
            # response.status_code != 2xx
            log_exception("PushNotificationManager", e)
        except Exception as e:
            log_exception("PushNotificationManager", e)
