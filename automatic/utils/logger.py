
import logging

LOGGER_AUTOMATIC = "Automatic"
LOGGER_SELENIUM = "Selenium"
LOGGER_WIN32 = "Win32"

class Logger:
    @classmethod
    def init(cls, name, level):
        logger = logging.getLogger(name)
        logger.setLevel(level)
        logger.handlers.clear()

        ch = logging.StreamHandler()
        ch.setLevel(level)  # handler의 레벨도 DEBUG로 설정
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        ch.setFormatter(formatter)
        logger.addHandler(ch)

    @classmethod
    def get(cls, name):
        return logging.getLogger(name)