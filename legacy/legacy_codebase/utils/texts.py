import html
import re
from typing import List
import aiogram.utils.markdown as md
from aiogram import types
from aiogram.types import CallbackQuery, Message
from base.base_connectors import get_from_base
from module_7.handlers.pydentic_models import HistoryDetails
from utils.utils_lite import create_counter

HEADER_TEXT = "SHIP KZ у вас есть непрочитанное сообщение"


def make_text_safe(input_text):
    safe_text = html.escape(input_text)
    return safe_text


def spammer_text_poshlina():
    text = md.text(
        md.text('<b>Новости про беспошлинный лимит</b>'),
        md.text(' '),
        md.text('До 1 апреля 2024 года можно ввозить товары из зарубежных интернет-магазинов'
                ' на территорию ЕАЭС (Россия, Беларусь, Армения, Казахстан и Кыргызстан)'
                ' на сумму до 1000 евро без пошлины. Если превысить эту сумму, придётся заплатить 15% от лишнего.'),
        md.text('Этот лимит уже трижды продлевали. Шансы на очередное продление есть, но и Минфин высказывает '
                'возражения (https://t.me/banksta/48304).'
                ' Возможно, лимит снова снизят до 200 евро.'),
        md.text(' '),
        md.text(' '),
        md.text('Так что если у вас в планах крупная покупка, лучше оформить её сейчас, чтобы посылка успела пройти '
                'таможню до 1 апреля.'),
        sep='\n'
    )

    return text


"""
Друзья, как и предполагалось, порог пошлины в 1 тыс. евро не продлили.
Подтверждение опубликовано
 (https://eec.eaeunion.org/news/1-aprelya-zakonchilsya-period-deystviya-vremennykh-povyshennykh-norm-besposhlinnogo-vvoza-tovarov-dl/) на сайте ЕЭК.

Это означает, что пошлина будет рассчитываться также, как это происходило до марта 2022 года: 15% от суммы превышения порога в 200 евро.
То есть, если товары в посылке стоят, например, 300 евро, нужно будет заплатить 15% от 100 евро.
"""


def spammer_text_poshlina2():
    text = md.text(
        md.text("Друзья, как и предполагалось, порог пошлины в 1 тыс. евро не продлили."),
        md.text("Подтверждение",
                md.link("опубликовано",
                        "https://eec.eaeunion.org/news/1-aprelya-zakonchilsya-period-deystviya-vremennykh-povyshennykh-norm-besposhlinnogo-vvoza-tovarov-dl/"),
                "на сайте ЕЭК.", sep=' '),
        md.text('Это означает, что пошлина будет рассчитываться также, как это происходило до марта 2022 года: 15% '
                'от суммы превышения порога в 200 евро. То есть, если товары в посылке стоят, например, 300 евро, '
                'нужно будет заплатить 15% от 100 евро.'),
        sep='\n')
    return text

def make_crypto_text():
    text = md.text(
        md.text("С сентября начинаем принимать платежи за заказы  в USDT (TRC20)."
                " Пока в ручном режиме и только в телеге,"
                " на сайте программист должен внести изменения."),
        md.text(" "),
        md.text("Порядок оформления обычный, только пишите менеджеру что хотите оплатить заказ в USDT."),
        md.text(" "),
        md.text("Комиссия за выкуп и транзит при таком способе оплаты будет 15%."),
        md.text(" "),
        md.text("Крипту принимаем только для обычных заказов, для групповых по прежнему в рублях."),
        sep="\n"
    )
    return text


def make_friday_text():
    text = md.text(
        md.text('Черная пятница на  tradeinn.com.'),
        md.text('Ловите промокод на скидку  15% - <b>BF15!</b>'),
        md.text(' '),
        md.text('<i>Заказ делается на вашем аккаунте, соответственно он должен быть и адрес ваш должен быть заполнен. '
                'Магазин отправляет товары напрямую в РФ. Сроки доставки 3-4 недели. Кроме того, поскольку мы '
                'оплачиваем заказы на вашем аккаунте у вас есть дополнительный кэшбек 1% в виде COINNS.</i>'),
        md.text(' '),
        md.text("Гайд по регистрации и особенностям сайта <a href='https://t.me/shipKZ/74'>тут</a>."),
        md.text(" "),
        md.text("<a href='https://t.me/shipKZ/73'>Порядок приобретения продукции "
                "Garmin/Shimano/Atomic/Salomon/Asics/Osprey/Suunto/RockShox</a>"),
        md.text(" "),
        md.text(" "),
        md.text("Наша комиссия на Tradeinn.com зависит от суммы всех ваших заказов, включая текущий:"),
        md.text("🔹 до 100k - 10%"),
        md.text("🔹 от 100к до 200k - 8%"),
        md.text("🔹 от 200к - 7%"),
        md.text("Минимальная комиссия 500 руб."),
        sep="\n")
    return text


def make_friday_mistakes():
    text = md.text(
        md.text("Ошибочка вышла."),
        md.text("Верный промокод на скидку 15% - <b>15BF</b>"),
        sep="\n"
    )

    return text


def make_no_discount_text(money):
    text = md.text(
        md.text('<b>Накопительные скидки при оплате на сайте Tradeinn</b>'),
        md.text(' '),
        md.text('Мы рады, что вы с нами и заказываете товары на Tradeinn.com с нашей помощью.'),
        md.text(' '),
        md.text('Комиссия по оплате будет зависеть от суммы всех ваших заказов, включая текущий:'),
        md.text(' '),
        md.text('🔹 до 100k - 10%'),
        md.text('🔹 от 100к до 200k - 8%'),
        md.text('🔹 от 200к - 7%'),
        md.text(' '),
        md.text(f'Вы заказали товаров на сумму {money} тыс.руб. Ваша комиссия пока 10%, но это легко поправить!'),
        md.text(' '),
        md.text('<b>ДО 1 АВГУСТА ВЫ МОЖЕТЕ СДЕЛАТЬ ЗАКАЗЫ С КОМИССИЕЙ 8%!</b>'), sep='\n')
    return text




def make_discount_text(discount):
    text = md.text(
        md.text('<b>Накопительные скидки при оплате на сайте Tradeinn</b>'),
        md.text(' '),
        md.text('Мы рады, что вы с нами и заказываете товары на Tradeinn.com с нашей помощью.'),
        md.text(' '),
        md.text('Комиссия по оплате будет зависеть от суммы всех ваших заказов, включая текущий:'),
        md.text(' '),
        md.text('🔹 до 100k - 10%'),
        md.text('🔹 от 100к до 200k - 8%'),
        md.text('🔹 от 200к - 7%'),
        md.text(' '),
        md.text(f'<b>ВАША КОМИССИЯ ПРИ ОПЛАТЕ - {discount}%</b>'), sep='\n')
    return text


def make_text_hello(username):
    text_hello = md.text(
        md.text("🫱   Добро пожаловать,", "*", username, "*", "!", "Я Бот-Помощник."),
        md.text(" "),
        md.text("🔸  Могу оформить заказ , в разделе 'Сделать заказ'."),
        md.text(""),
        md.text("🔸  Ответы на большинство вопросов и калькулятор стоимости в разделе 'Kонсультация'."),
        md.text(" "),
        md.text(
            "🗣  В случае необходимости, и, если раздел консультаций не помог, для связи с живым консультантом просто "
            "пишите в чат. "),
        sep="\n"
    )
    return text_hello


def thank_u():
    text = md.text(
        md.text("🔶 Благодарим за заказ! 🔶"),
        md.text(" "),
        md.text("Будем рады дальнейшему сотрудничеству."
                " Если вам понравился наш сервис, оставьте отзыв в канале"
                " https://t.me/shipkz_discussing."),
        md.text(" "),
        sep="\n",
    )
    return text


def make_text_for_FAQ(value: str):
    try:
        with open("storages" + value + ".html", "r", ) as fi:
            result = fi.read()
            fi.close()
    except Exception as ex:
        print("чето пошло не так")
    return result


def make_user_info_report(query: CallbackQuery, order_id=None) -> md.text():
    user_id = query.from_user.id
    user_first_name = query.from_user.first_name
    user_second_name = query.from_user.last_name
    username = query.from_user.username
    result = md.text(
        md.text(f" #{order_id}"),
        md.text(f"Type: <b>{query.data}</b>"),
        md.text(f"User: ", md.hlink(f"#ID_{user_id}", f"tg://user?id={user_id}")),
        md.text(f"First Name: {user_first_name}"),
        md.text(f"Second Name: {user_second_name}"),
        md.text(f"UserName :  @{username}"),
        sep="\n"
    )
    return result


def make_user_info_report_from_message(message: types.Message):
    user_id = message.from_user.id
    user_first_name = make_text_safe(message.from_user.first_name)
    user_second_name = make_text_safe(message.from_user.last_name)
    result = md.text(
        md.text(f"#ID_{user_id}"),
        md.text(f"First Name: {user_first_name}"),
        f"|",
        md.text(f"Second Name: {user_second_name}"),
        sep="\n"
    )
    return result


def add_orders_to_mask(id, mask: list) -> list:
    """добавляет в маску активные ордера если они есть"""
    stmt = f"""SELECT order_status.order_id, order_status.manager_id FROM orders 
                JOIN order_status ON orders.id = order_status.order_id
                WHERE order_status.status = true
                AND orders.client = {id}
                ORDER BY order_status.order_id DESC;"""
    query_set = get_from_base(stmt)
    count = 1
    if query_set:
        for order in query_set:
            if count >= 10:
                break
            order_str = "/order_" + str(order[0])
            manager_str = str([order[1]]).replace("'", "")
            if manager_str != '[None]':
                order_id = order[0]

                stmt2 = f"""SELECT managers.short_name FROM order_status
                                JOIN managers ON order_status.manager_id = managers.user_id
                                WHERE order_status.order_id = {order_id}"""

                short_name = get_from_base(stmt2)[0][0]
                manager_str = "[" + str(short_name) + "]"
            mask.append(order_str + " | " + manager_str)
            count += 1
    return mask


def get_mask_from_message(text_to_parce):
    """ маска со стороны менеджеров """

    text_to_parce = make_text_safe(text_to_parce)
    result = []
    id = get_id_from_text(text_to_parce)
    text_to_parce = text_to_parce.split("\n")
    result.append(f"#ID_{id}")
    result.append(text_to_parce[1])
    result = add_orders_to_mask(id, result)
    return result


def get_mask_from_web_message(text_to_parce, user_id):
    text_to_parce = make_text_safe(text_to_parce)
    result = []
    text_to_parce = text_to_parce.split("\n")
    result.append(f"#WEB_{user_id}")
    result.append(text_to_parce[1])
    return result


def make_mask_to_messages(income, user_id):
    """это делает маску со стороны юзеров"""
    assert isinstance(income, types.Message) or isinstance(income, types.CallbackQuery)
    user_first_name = income.from_user.first_name
    user_second_name = income.from_user.last_name
    result = [
        md.text(f"#ID_{user_id}"),
        md.text(f"{user_first_name}",
                f"|",
                f"{user_second_name}",
                )]
    result = add_orders_to_mask(user_id, result)
    result = md.text(*result, sep="\n")
    #FIXME if some going wrong
    result = html.escape(result)
    return result


def make_mask_to_messages_w(income, user_id):
    """это делает маску со стороны юзеров"""
    assert isinstance(income, types.Message) or isinstance(income, types.CallbackQuery)
    user_first_name = income.from_user.first_name
    user_second_name = income.from_user.last_name
    username = income.from_user.username
    result = [
        md.text(f"#WEB_{user_id}"),
        md.text(f"{username}", )
    ]
    result = add_orders_to_mask(user_id, result)
    result = md.text(*result, sep="\n")
    return result


def order_answer_vocabulary(income, order_id):
    match income:
        case 'KAZ_ORDER_LINKS':
            text = ['Вариант 1', f'Заказ через Казахстан №{order_id}', 'ссылки']
        case 'KAZ_ORDER_CABINET':
            text = ['Вариант 1', f'Заказ через Казахстан №{order_id}', 'доступ в кабинет']
        case 'TRADEINN':
            text = ['Вариант 2', f'Заказ через TradeInn №{order_id}']
        case 'PAYMENT':
            text = ['Вариант 3', f'Выкуп через посредника №{order_id}']
    return text


def make_links_info_text(links):
    counter = create_counter()
    md_obj = [md.hlink("ссылка " + str(counter()), link) for link in links]
    return md_obj


def get_vaflalist(pos=1):
    if pos == 1:
        result = ('первая',
                  'вторая',
                  'третья',
                  'четвертая',
                  'пятая',
                  'шестая',
                  'седьмая',
                  'восьмая',
                  'девятая',
                  'десятая',
                  'одиннадцатая',
                  'двенадцатая',
                  'тринадцатая',
                  'четырнадцатая',
                  'пятнадцатая')
    elif pos == 2:
        result = ('первой',
                  'второй',
                  'третьей',
                  'четвертой',
                  'пятой',
                  'шестой',
                  'седьмой',
                  'восьмой',
                  'девятой',
                  'десятой',
                  'одиннадцатой',
                  'двенадцатой',
                  'тринадцатой',
                  'четырнадцатой',
                  'пятнадцатой',)
    return result


def get_additional_from_proxi(data):
    """Не помню уже видимо что то связанное с созданием текста в ордере"""
    print("data " * 10, data, sep="\n")
    addition = []
    hrefs = [data.get(key) for key in [('href_' + str(key)) for key in
                                       [i for i in range(1, data.get('num') + 1)]]]
    comments = [data.get(key) for key in
                [('comment_' + str(key)) for key in
                 [i for i in range(1, data.get('num') + 1)]]]
    link = iter(make_links_info_text(hrefs))
    comment = iter(comments)
    addition.append(md.text('shop: ', f"<code>{data['shop']}</code>"))
    for _ in hrefs:
        new = md.text(next(link), ": ", f"{next(comment)}")
        addition.append(new)
    return addition


def get_id_from_text(text):
    id = re.search(r"#ID_(\d+)", text)
    if id:
        return id.group(1)
    else:
        return None


class TheWay:
    def __init__(self, id, way):
        self.id = id
        self.way = way

    def __repr__(self):
        return f"THE WAY variables: {self.id} | {self.way}"


def find_the_way(message: types.Message,text_mode=False) -> TheWay | None:
    print('start find way')
    if text_mode:
        text = message
    else:
        text = message.reply_to_message.text
    print(text)
    id = re.search(r"#ID_(\d+)", text)
    if id:
        print('teleway')
        result = TheWay(id.group(1), 'Telegram way')
        return result
    id2 = re.search(r"#WEB_(\d+)", text)
    if id2:
        print('webway')
        result = TheWay(id2.group(1), 'Web way')
        return result
    else:
        return None



def make_message_text(message: list) -> md.text():
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

        result.append(md.text(pointer, body, sep=" "))
        result.append(md.text(" "))

    for is_answer, body in after:
        if is_answer:
            pointer = ''
        else:
            pointer = '👈'
        if len(str(body)) >= 80:
            insert_text = str(body)[:60] + "..."
        else:
            insert_text = str(body)
        result.append(md.text(pointer, insert_text, sep=" "))
    return result


def preparing_message_list(income: List[HistoryDetails]) -> List:
    result = []
    for row in income:
        result.append((row.is_answer, row.time, row.text, row.is_read))
    return result


def preparing_for_message_5list(income):
    result = []
    for row in income:
        result.append((row.is_answer, row.text, row.is_read))
    return result


def make_message_text_w(message: list) -> md.text():
    result = []
    before = message[:1]
    after = message[1:]

    for is_answer, body, is_read in before:
        if is_answer:
            eye = get_eye(is_read)
            pointer = "✅" + eye
            if len(body) > 50:
                if is_read:
                    body = str(body[:50]) + "..."
                else:
                    body = str(body[:50]) + "..."
        else:
            pointer = "🆘"
        result.append(md.text(pointer, body, sep=" "))
        result.append(md.text(" "))
    for is_answer, body, is_read in after:
        if is_read:
            eye = "👁"
        else:
            eye = ""
        if is_answer:
            pointer = '👉' + eye
        else:
            pointer = '👈'
        if len(str(body)) >= 80:
            insert_text = str(body)[:60] + "..."
        else:
            insert_text = str(body)
        result.append(md.text(pointer, insert_text, sep=" "))
    return result


def get_eye(is_read):
    if is_read:
        return "👁"
    else:
        return ""


def make_message_text_full(message: list) -> md.text():
    message = check_lenght(message)
    result = []
    before = message[:1]
    after = message[1:]

    for is_answer, time, body in before:
        if is_answer:
            pointer = "✅"
        else:
            pointer = "🆘"
        result.append(md.text(pointer, time, body, sep=" "))
        result.append(md.text(" "))
    for is_answer, time, body in after:
        if is_answer:
            pointer = ''
        else:
            pointer = '👈'
        result.append(md.text(pointer, time, body, sep=" "))
    return result


def make_message_text_full_w(message: list) -> md.text():
    message = check_lenght(message)
    result = []
    before = message[:1]
    after = message[1:]

    for is_answer, time, body, is_read in before:
        eye = get_eye(is_read)
        if is_answer:
            pointer = "✅" + eye
        else:
            pointer = "🆘"
        result.append(md.text(pointer, time, body, sep=" "))
        result.append(md.text(" "))
    for is_answer, time, body, is_read in after:
        eye = get_eye(is_read)
        if is_answer:
            pointer = '👉' + eye
        else:
            pointer = '👈'
        result.append(md.text(pointer, time, body, sep=" "))
    return result


def check_lenght(text: list) -> list:
    while len(str(text)) > 3500:
        text.pop()
    return text


def look_at_site_text():
    """текст Пожалуйста у вас сообщение"""
    url = "https://shipkz.ru/"
    message = f"""\
    Уважаемый пользователь,

    У вас есть непрочитанное сообщение, на которое необходимо ответить. Пожалуйста, перейдите по следующей ссылке для просмотра сообщения:

    <a href='{url}'>Перейти к сообщению</a>

    С уважением,
    Команда shipkz.ru
    """
    return message