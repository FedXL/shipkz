
from django.conf import settings
from django.urls import reverse

from app_front.management.email.email_sender import send_email


def send_verification_email(to_mail,user, token):
    url  = reverse('confirm_email')
    url_host = settings.BASE_URL_HOST
    verification_link = f"{url_host}{url}?token={token}"
    email_body = (f'<p>Уважаемый пользователь {user}</p>'
                  f'<p>Пожалуйста, нажмите на ссылку ниже, чтобы подтвердить свой адрес электронной почты:</p>'
                  f'<a href="{verification_link}">Активировать учетную запись SHIPKZ</a>'
                  
                  f'<p>Если вы не запрашивали эту проверку, пожалуйста, проигнорируйте это письмо.</p>')
    send_email(header="ShipKZ активация учётной записи",body= email_body,to_mail=to_mail)
