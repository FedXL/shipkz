import datetime
import time

from celery import shared_task
from django.conf import settings

from app_auth.management.email_handler import send_verification_email, send_repair_password_email, \
    send_repair_password_email_2
from app_auth.models import Profile
from app_front.management.unregister_authorization.token import create_token


@shared_task
def send_verification_email_task(to_mail,user, token):
    send_verification_email(to_mail,user, token)

@shared_task
def send_repair_password_email_task(to_mail, token):
    if not to_mail:
        return "Error: to_mail is None"
    if not token:
        return "Error: token is None"
    send_repair_password_email(to_mail, token)


@shared_task
def repair_password_move_site(profile_id):
    profile = Profile.objects.get(id=profile_id)
    email = profile.email
    user = profile.user
    ip = '188.130.160.216'
    token  = create_token(username=user.username,
                                  user_id=user.id,
                                  timedelta=datetime.timedelta(hours=12),
                                  ip=ip, secret=settings.REPAIR_PASSWORD_SECRET)
    user.repair_verification_token = token
    user.save()
    send_repair_password_email_2(email, token)
    time.sleep(2)
    return 'success'