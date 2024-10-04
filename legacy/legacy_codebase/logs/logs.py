import logging


my_logger = logging.getLogger('my_logs')
my_logger.setLevel(logging.DEBUG)

handler_console = logging.StreamHandler()
handler_console.setLevel(logging.DEBUG)

handler_file = logging.FileHandler('webhook.log')
handler_file.setLevel(logging.DEBUG)

formatter = logging.Formatter('[%(asctime)s] [%(levelname)s] [%(module)s | %(funcName)s] %(message)s')
handler_console.setFormatter(formatter)



my_logger.addHandler(handler_console)
my_logger.addHandler(handler_file)