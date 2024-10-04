import asyncio
from typing import List
from aiogram import Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.types import CallbackQuery, ParseMode
import aiogram.utils.markdown as md
import datetime
from sqlalchemy import update
from sqlalchemy.orm import Session
from base.good_db_handlers import add_parce_task, add_user_to_base_good, create_order_bot
from base.models import OrderStatus
from create_bot import bot
from handlers.chat.sender import catch_messaging
from logs.bot_logger import bot_logger
from sheets.add_orders import add_last_string
from utils.config import orders_chat_storage, alerts, engine
from utils.markap_menu import SuperMenu
from utils.texts import make_user_info_report, order_answer_vocabulary, get_additional_from_proxi
from utils.utils_lite import create_new_message_order, quot_replacer


def check_parcer(order_id: int) -> List | None:
    bot_logger.debug(f'start with {order_id}')
    with Session(engine) as session:
        result = session.query(OrderStatus.order_price).filter(OrderStatus.order_id == order_id).one_or_none()
        bot_logger.debug(f'end check {result}')
        session.close()
    return result


async def make_order_answer(query: CallbackQuery, state: FSMContext):
    await query.answer("Успешно")
    await query.message.delete_reply_markup()
    await query.message.delete()
    income = query.data
    login_tradeinn, pass_tradeinn = False, False
    if income in ['KAZ_ORDER_LINKS', 'KAZ_ORDER_CABINET', 'PAYMENT']:
        is_kazakhstan = True
    else:
        is_kazakhstan = False
    match income:
        case "KAZ_ORDER_LINKS":
            async with state.proxy() as data:
                try:
                    addition = get_additional_from_proxi(data)
                except:
                    addition = "ERROR"
        case "KAZ_ORDER_CABINET":
            async with state.proxy() as data:
                addition = [
                    md.text('Магазин: ', f"<code>{data.get('shop')}</code>"),
                    md.text('Логин: ', f"<code>{data.get('log')}</code>"),
                    md.text('Пароль: ', f"<code>{data.get('pass')}</code>"),
                ]
        case "TRADEINN":
            async with state.proxy() as data:
                login_tradeinn = data.get('login')
                pass_tradeinn = data.get('pass')
                addition = [
                    md.text('Логин: ', f"<code>{login_tradeinn}</code>"),
                    md.text("Пaроль: ", f"<code>{pass_tradeinn}</code>")
                ]
                try:
                    marat_text = md.text(*addition, sep="\n")
                    await bot.send_message(chat_id=6215812561, text=marat_text,parse_mode=ParseMode.HTML)
                except Exception as er:
                    print(f'Error in send message to marat: {er}')
                print('[DEBUG]', addition)
                await bot.send_message(alerts, f"From {query.from_user.username} | {query.from_user.id} | NewOrder!")
        case "PAYMENT":
            async with state.proxy() as data:
                addition = [
                    md.text('Магазин: ', f"<code>{data.get('shop')}</code>"),
                    md.text('Логин: ', f"<code>{data.get('login')}</code>"),
                    md.text('Пароль: ', f"<code>{data.get('pass')}</code>"),
                ]
    await state.finish()

    ## ------------------------------- ADD TO BASE - ----------------------------------------

    new_str = quot_replacer(str(addition))
    await add_user_to_base_good(user_id=query.from_user.id,
                                is_kazakhstan=is_kazakhstan,
                                user_first_name=query.from_user.first_name,
                                user_second_name=query.from_user.last_name,
                                username=query.from_user.username)

    try:
        order_id = await create_order_bot(client=query.from_user.id,
                                          order_type=income,
                                          order_body=new_str)

        new_message = create_new_message_order(query, income, order_id)
        await catch_messaging(new_message)
        if income == "TRADEINN":
            bot_logger.debug(f'Add parce task to order {order_id}')
            await add_parce_task(order_id=order_id, login=login_tradeinn, psw=pass_tradeinn, task_type='TRADEINN')
    except Exception as er:
        order_id = False
        bot_logger.error(f"Unexpect error: {er}")
    user_info = make_user_info_report(query, order_id)
    pre_additional = order_answer_vocabulary(income, order_id)
    await_message = await bot.send_message(query.from_user.id, "Нам надо проверить данные.")
    await asyncio.sleep(2)
    time = 0

    # ----------------------------Tradeinn--------------------------------------------------
    if income == 'TRADEINN':
        # прости меня господи за этот код:
        while True:
            print("[INFO]", 'start прости господи за этот код')
            if 30 > time >= 0:
                textss = "Проверям данные. "
            elif 60 > time >= 30:
                textss = "Проверям, мы на пол пути. "
            elif 90 > time >= 60:
                textss = "Осталось чуть-чуть. "
            elif 200 > time >= 90:
                textss = "Видимо вы не первый в очереди, придется еще подождать."
            elif time > 200:
                textss = "Успех"
                await await_message.edit_text(f"{textss}")
                await bot.send_message(orders_chat_storage, md.text(
                    md.text('parcing long ERROR 200 sec left and nothing'),
                    md.text(user_info),
                    md.text(*addition, sep="\n"),
                    sep="\n"),
                                       disable_web_page_preview=True,
                                       parse_mode=ParseMode.HTML)

                await bot.send_message(query.from_user.id, md.text(
                    md.text("Ваш заказ успешно принят."),
                    md.text(*pre_additional, sep="\n"),
                    md.text(*addition, sep="\n"),
                    sep="\n"),
                                       reply_markup=SuperMenu.cancel,
                                       disable_web_page_preview=True,
                                       parse_mode=ParseMode.HTML)
                break

            await asyncio.sleep(5)
            time += 5
            await await_message.edit_text(f"{textss}...{time}/100")
            price = check_parcer(order_id)[0]
            print(price)

            # ----------------------------------кривой пароль
            if price == "Incorrect password":
                delete_order_from_head(order_id)
                await await_message.edit_text((
                    f"У меня не получилсь войти в личный кабинет😔😔😔 \nСкорее всего неправильный пароль или логин \nВаши данные:"))
                await bot.send_message(query.from_user.id, md.text(
                    md.text(*addition, sep="\n"),
                    sep="\n"), parse_mode=ParseMode.HTML)
                await bot.send_message(orders_chat_storage, md.text(
                    md.text('Неправильный пароль'),
                    md.text(user_info),
                    md.text(*addition, sep="\n"),
                    sep="\n"),
                                       disable_web_page_preview=True,
                                       parse_mode=ParseMode.HTML)
                break
            ##----------------------------------- в ордер статусе ниче нет
            elif price is None:
                continue
            ##------------------------------------ все окей
            elif type(price) == str and price != 'ERROR':
                await await_message.delete()
                await bot.send_message(query.from_user.id, md.text(
                    md.text("Ваш заказ успешно принят."),
                    md.text(*pre_additional, sep="\n"),
                    md.text(*addition, sep="\n"),
                    sep="\n"),
                                       reply_markup=SuperMenu.cancel,
                                       disable_web_page_preview=True,
                                       parse_mode=ParseMode.HTML)
                await bot.send_message(orders_chat_storage,
                                       md.text(md.text(user_info),
                                               md.text(*addition, sep="\n"),
                                               sep="\n"),
                                       disable_web_page_preview=True,
                                       parse_mode=ParseMode.HTML)
                try:
                    await add_last_string(
                        [(order_id, query.from_user.id, str(datetime.datetime.now()), income, new_str)],
                        'orders_storage')
                    if income in ['KAZ_ORDER_LINKS', 'KAZ_ORDER_CABINET']:
                        await add_last_string(
                            [(order_id, query.from_user.id, str(datetime.date.today()), income, new_str)],
                            'Dashboard')
                except Exception as ER:
                    print(f"[ERROR] google sheets error in orders callback: {ER}")
                break
            ##------------------------------------------------------ОШИБКА
            elif price == 'ERROR':
                delete_order_from_head(order_id)
                await await_message.edit_text('Успешно')
                await bot.send_message(orders_chat_storage, md.text(
                    md.text('Parcing ERROR'),
                    md.text(user_info),
                    md.text(*addition, sep="\n"),
                    sep="\n"),
                                       disable_web_page_preview=True,
                                       parse_mode=ParseMode.HTML)

                break
    # ----------------------------------------ВСЁ остальное------------------------------------------------------------

    else:
        await bot.send_message(query.from_user.id, md.text(
            md.text("Ваш заказ успешно принят."),
            md.text(*pre_additional, sep="\n"),
            md.text(*addition, sep="\n"),
            sep="\n"),
                               reply_markup=SuperMenu.cancel,
                               disable_web_page_preview=True,
                               parse_mode=ParseMode.HTML)

        await bot.send_message(query.from_user.id,
                               "Теперь ожидайте ответа менеджера через бота, Вам обязательно ответят. Мы стараемся "
                               "отвечать в течении часа.")

        await bot.send_message(orders_chat_storage,
                               md.text(md.text(user_info),
                                       md.text(*addition, sep="\n"),
                                       sep="\n"),
                               disable_web_page_preview=True,
                               parse_mode=ParseMode.HTML)
        try:
            await add_last_string([(order_id, query.from_user.id, str(datetime.datetime.now()), income, new_str)],
                                  'orders_storage')
            if income in ['KAZ_ORDER_LINKS', 'KAZ_ORDER_CABINET']:
                await add_last_string([(order_id, query.from_user.id, str(datetime.date.today()), income, new_str)],
                                      'Dashboard')

        except Exception as ER:
            print(f"[ERROR] google sheets error in orders callback: {ER}")


def delete_order_from_head(order_id: int):
    print('[INFO] start delete_order_from_head')
    try:
        with Session(engine) as session:
            is_head = session.query(OrderStatus).filter(OrderStatus.order_id == order_id).scalar()
            if is_head:
                status = False
            else:
                status = True
            stmt = update(OrderStatus).filter(OrderStatus.order_id == order_id).values(status=status)
            session.execute(stmt)
            session.commit()
            print(f'[INFO] success the {order_id} provide status {status}')
    except Exception as ER:
        print(f'delete_order_from_head Error {ER}')


def register_handlers_save_order(dp: Dispatcher):
    dp.register_callback_query_handler(make_order_answer,
                                       lambda c: c.data in ['KAZ_ORDER_LINKS', 'KAZ_ORDER_CABINET', 'TRADEINN',
                                                            'PAYMENT'],
                                       state="*")
