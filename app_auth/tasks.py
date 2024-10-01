from celery import shared_task

from app_auth.management.email_handler import send_verification_email


@shared_task
def send_verification_email_task(to_mail,user, token):
    send_verification_email(to_mail,user, token)