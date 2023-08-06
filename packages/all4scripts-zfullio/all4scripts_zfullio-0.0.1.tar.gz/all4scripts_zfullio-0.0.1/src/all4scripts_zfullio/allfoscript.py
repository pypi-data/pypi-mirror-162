"""Библиотеки помогающие в создании скрипта"""
from datetime import datetime

from loguru import logger
from notifiers import get_notifier


class Script:
    date_start: datetime = datetime.now()

    def __init__(self, name: str):
        self.name: str = name
        self.manual_mode: bool = False
        self.options_restart: bool = True
        logger.add("logs/logs.log", level="DEBUG", format="{time} {level} {message}",
                   rotation="1 week")
        logger.info(f"{self.name}: Скрипт запущен")


class Notice:
    telegram = get_notifier("telegram")

    def __init__(self, name_program: str, token: str, chat_id: str, admin_chat: str, status=True, admin=None):
        if admin is None:
            self.admin = []
        self.name_program: str = name_program
        self.token: str = token
        self.chat_id: str = chat_id
        self.admin_chat_id: str = admin_chat
        self.status: bool = status
        self.admin: str = admin
        self.start_program()

    def start_program(self) -> None:
        if self.status:
            self.telegram.notify(message=f"{self.name_program}: Скрипт запущен",
                                 token=self.token, chat_id=self.admin_chat_id)

    def notify(self, message, debug_info=False) -> None:
        if self.status and not debug_info:
            self.telegram.notify(message=message, token=self.token, chat_id=self.chat_id)
        else:
            logger.info("Уведомления отключены")

    def critical(self, message) -> None:
        logger.critical(f"{self.name_program}: Возникла критическая ошибка. {message}")
        if self.status:
            self.telegram.notify(message=f"{self.admin} {self.name_program}: Скрипт мог быть остановлен. Причина: "
                                         f"{message}", token=self.token, chat_id=self.admin_chat_id)
        else:
            logger.info("Уведомления отключены")
