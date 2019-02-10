import os
import logging

from py_vapid import Vapid01 as Vapid
from py_vapid import b64urlencode
from cryptography.hazmat.primitives import serialization
from pywebpush import webpush, WebPushException

from byemail.conf import settings

logger = logging.getLogger(__name__)

def send_web_push(subscription_information, message_body):
    try:
        return webpush(
            subscription_info=subscription_information,
            data=message_body,
            vapid_private_key=settings.VAPID_PRIVATE_KEY,
            vapid_claims=settings.VAPID_CLAIMS
        )
    except WebPushException as ex:
        logger.exception("Exception while trying to send push notification")

        if ex.response and ex.response.json():
            extra = ex.response.json()
            logger.info("Remote service replied with a %s:%s, %s",
                extra.code,
                extra.errno,
                extra.message
            )

def get_application_server_key():
    """
    Get and prepare application server_key
    """

    vapid = Vapid.from_file(settings.VAPID_PRIVATE_KEY)
    raw_pub = vapid.public_key.public_bytes(serialization.Encoding.X962, serialization.PublicFormat.UncompressedPoint)

    return b64urlencode(raw_pub)

# To generate with openssl command line
# See https://mushfiq.me/2017/09/25/web-push-notification-using-python/
# openssl ecparam -name prime256v1 -genkey -noout -out vapid_private.pem
# openssl ec -in vapid_private.pem -pubout -out vapid_public.pem
# openssl ec -in ./vapid_private.pem -outform DER|tail -c +8|head -c 32|base64|tr -d '=' |tr '/+' '_-' >> private_key.txt
# openssl ec -in ./vapid_private.pem -pubout -outform DER|tail -c 65|base64|tr -d '=' |tr '/+' '_-' >> public_key.txt

