import datetime
from app_bot.management.bot_models import HistoryDetails
from legacy.models import WebUsers, WebMessages, WebPhotos, WebDocs

def make_mask_to_web_messages(user_id, user_name) -> str:
    """это делает маску со стороны юзеров с использованием HTML разметки"""
    result = f"<b>#WEB_{user_id}</b>\n{user_name}\n"
    return result

def download_history_from_web_message(web_user: WebUsers, is_for_meeting_message=False) -> list[HistoryDetails]:
    history = []
    web_messages = WebMessages.objects.filter(user=web_user).order_by('-time')[:5]

    for message in web_messages:
        message_dict = message.as_dict()
        message_dict['user_name'] = message.user.web_username
        history_row = HistoryDetails(**message_dict)
        if history_row.is_answer and not is_for_meeting_message:
            text_splited = history_row.text.split(':', 1)
            if len(text_splited) > 1:
                manager_name = text_splited[0]
                history_row.user_name = manager_name
                history_row.text = text_splited[1]

        if not is_for_meeting_message:
            if history_row.message_type == 'photo':
                photo = WebPhotos.objects.filter(message=message).first()
                if photo:
                    history_row.text = photo.photo_path
                else:
                    history_row.text = 'Фото удалено'
            elif history_row.message_type == 'document':
                document = WebDocs.objects.filter(message=message).first()
                history_row.text = document.doc_path
        else:
            original_date = history_row.time
            original_date_with_year = "2024, " + original_date
            parsed_date = datetime.datetime.strptime(original_date_with_year, "%Y, %B %d, %H:%M")
            formatted_date = parsed_date.strftime("%d-%m %H:%M")
            history_row.time = formatted_date
        history.append(history_row)
    return history


def make_message_text_web_version(message: list) -> list:
    result = []
    before = message[:1]
    after = message[1:]

    for is_answer, body in before:
        if is_answer:
            pointer = "✅"
            if len(body) > 50:
                body = str(body[:50]) + "..."
        else:
            pointer = "🆘"

        result.append(f"{pointer} {body}\n")

    for is_answer, body in after:
        if is_answer:
            pointer = ''
        else:
            pointer = '👈'
        if len(str(body)) >= 80:
            insert_text = str(body)[:60] + "..."
        else:
            insert_text = str(body)
        result.append(f"{pointer} {body}\n")
    return result



def create_web_message_text(web_user:WebUsers):
    history = download_history_from_web_message(web_user=web_user)
    history = history[:5]
    history_prep = [(mes.is_answer, mes.text,) for mes in history]
    mask = make_mask_to_web_messages(user_id=web_user.user_id, user_name=web_user.web_username)
    text = make_message_text_web_version(history_prep)
    text_to_send = mask
    for item in text:
        text_to_send += item
    return text_to_send