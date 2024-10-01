import smtplib
from email.mime.text import MIMEText
from email.header import Header
from email.mime.multipart import MIMEMultipart
from email.utils import formatdate
import logging
my_logger = logging.getLogger('email_sender')
my_logger.setLevel(logging.DEBUG)
my_logger.addHandler(logging.StreamHandler())
my_logger.addHandler(logging.FileHandler('email_sender.log'))


def send_email(header, body, to_mail):

    my_logger.debug('Start send_email')
    my_logger.debug(f'header: {header}')
    my_logger.debug(f'body: {body}')
    my_logger.debug(f'to_mail: {to_mail}')

    try:
        from_mail = "shipkz.ru@gmail.com"
        # from_mail = "fedorkuruts@gmail.com"
        from_passwd = "rfmd tols ggcv vbqo"
        # from_passwd = "ppuc icbr vbxs pckz"
        server_adr = "smtp.gmail.com"
        port = 587
        msg = MIMEMultipart()
        msg["From"] = from_mail
        msg['To'] = to_mail
        msg["Subject"] = Header(header, 'utf-8')
        msg["Date"] = formatdate(localtime=True)
        msg.attach(MIMEText(body, 'html', 'utf-8'))

        my_logger.debug('Создали сообщение')
        smtp = smtplib.SMTP(server_adr, port=port)
        my_logger.debug('создали объект для отправки сообщения')
        smtp.starttls()
        my_logger.debug('Открвываем сединение')
        smtp.ehlo()
        smtp.login(from_mail, from_passwd)
        my_logger.debug('Залогинился в свой ящик')
        smtp.sendmail(from_mail, to_mail, msg.as_string())
        server_response = smtp.noop()
        my_logger.info(f'Ответ сервера {server_response}')
        print(f'Ответ сервера {server_response}')
        smtp.quit()
        my_logger.info('Email was sent successfully!!')
        return True
    except Exception as e:
        my_logger.error(f'Error in send_email: {e}')
        return False

