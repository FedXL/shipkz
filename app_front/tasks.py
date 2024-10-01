from celery import shared_task
from app_front.management.email.email_sender import send_email


@shared_task
def send_email_task(header, body, to_mail):
    send_email(header, body, to_mail)