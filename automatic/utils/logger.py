
import logging

AUTOMATIC_LOGGER_NAME = "Automatic"


def init_logger(loglevel=logging.INFO):
    logger = logging.getLogger(AUTOMATIC_LOGGER_NAME)
    logger.setLevel(loglevel)

    ch = logging.StreamHandler()
    ch.setLevel(loglevel)  # handler의 레벨도 DEBUG로 설정
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    ch.setFormatter(formatter)
    logger.addHandler(ch)


def get_logger():
    return logging.getLogger(AUTOMATIC_LOGGER_NAME)
