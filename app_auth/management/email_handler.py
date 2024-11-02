
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

def send_repair_password_email(to_mail,token):
    url  = reverse('repair_password_message')
    url_host = settings.BASE_URL_HOST
    verification_link = f"{url_host}{url}?token={token}"
    email_body = (f'<p>Для восстановления пароля перейдите по ссылке:</p>'
                  f'<a href="{verification_link}">Восстановить пароль</a>'
                  f'<p>Если вы не запрашивали восстановление пароля, пожалуйста, проигнорируйте это письмо.</p>')
    send_email(header="ShipKZ восстановление пароля",body= email_body,to_mail=to_mail)


def send_repair_password_email_2(to_mail, token):
    url = reverse('repair_password_message')
    url_host = settings.BASE_URL_HOST
    verification_link = f"{url_host}{url}?token={token}"
    email_body = (f'<p>Здравствуйте!</p>'
                  f'<p>Мы обновили наш сайт ShipKZ и приглашаем вас снова ввести или обновить пароль для вашего аккаунта.</p>'
                  f'<p>Пожалуйста, перейдите по следующей ссылке, чтобы установить новый пароль:</p>'
                  f'<a href="{verification_link}">Восстановить пароль</a>'
                  f'<br><br>'
                  f'<p>Спасибо, что остаетесь с нами!</p>')
    send_email(header="Обновление пароля для ShipKZ", body=email_body, to_mail=to_mail)
