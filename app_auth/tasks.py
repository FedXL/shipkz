from celery import shared_task
from app_auth.management.email_handler import send_verification_email, send_repair_password_email

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