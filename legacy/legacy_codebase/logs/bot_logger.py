import logging

bot_logger = logging.getLogger('bot_logs')
bot_logger.setLevel(logging.DEBUG)

# Создаем файловый обработчик и указываем путь к файлу
handler_file = logging.FileHandler('bot.log')
handler_file.setLevel(logging.DEBUG)

formatter = logging.Formatter('[%(asctime)s] [%(levelname)s] [%(module)s | %(funcName)s] %(message)s')
handler_file.setFormatter(formatter)

bot_logger.addHandler(handler_file)