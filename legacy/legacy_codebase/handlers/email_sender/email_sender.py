import datetime
import smtplib
import time
from email.mime.text import MIMEText
from email.header import Header
from email.mime.multipart import MIMEMultipart
from email.utils import formatdate
from sqlalchemy import select
from sqlalchemy.orm import Session
from base.good_db_handlers import get_email_by_user_id, check_was_last_message_read
from base.models import EmailTask, EmailTaskStatus
from logs.logs import my_logger
from utils.config import async_engine_bot, orders_chat_storage, engine
from utils.errors import send_message_from_bot_synch
from utils.texts import look_at_site_text


def send_email(header, body, to_mail):
    try:
        my_logger.info('Start send email')
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
        send_message_from_bot_synch(orders_chat_storage,
                                    f'[EMAIL SENDER ERROR] Не удалось отправить почту to {to_mail}   {str(e)}')
        return False


def execute_email_tasks():
    """function to execute send email tasks from email task table"""
    time_now = datetime.datetime.now()
    with Session(engine) as session:
        print('start execute email tasks')
        stmt = select(EmailTask).where(EmailTask.status == 'await')
        result = session.execute(stmt)
        tasks = result.scalars().all()
        if tasks:
            print(f'we have a {len(tasks)}')
            for task in tasks:
                is_eye = check_was_last_message_read(user_id=task.web_user, session=session)
                if is_eye:
                    print('а уже посмотрели')
                    task.status = EmailTaskStatus.CANCELED
                    print(task)
                    continue
                else:
                    print(' Не просмотрено фигачим письмо')
                print(task.web_user)
                execute_time = task.execute_time
                print('time now', time_now)
                print('execute time', execute_time)
                if execute_time < time_now:
                    text = look_at_site_text()
                    header = task.header
                    to_mail = get_email_by_user_id(user_id=task.web_user, session=session)
                    if not to_mail:
                        task.status = EmailTaskStatus.CANCELED
                        continue
                    was_send = send_email(body=text,
                                          header=header,
                                          to_mail=to_mail)
                    time.sleep(10)
                    if was_send:
                        print('was send')
                        send_message_from_bot_synch(orders_chat_storage,
                                                    f'[EMAIL SENDER][SUCCESS] mail was send to {to_mail}')
                        task.status = EmailTaskStatus.EXECUTED
                    else:
                        print('wasn t send')
                        task.status = EmailTaskStatus.CANCELED
            session.commit()
