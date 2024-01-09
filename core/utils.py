import threading
import time
from pathlib import Path

import schedule
from pyrogram import Client
from pyrogram.enums import ParseMode
from pyrogram.errors import AuthKeyUnregistered

from core import settings


class FilesManager:
    current_receiver_index = 0
    _message_text = None

    @staticmethod
    def get_file(path):
        if not Path(path).exists():
            Path.touch(path)
        return path

    def add_receiver(self, chat_id: int):
        try:
            with open(
                    self.get_file(settings.RECEIVERS_FILE),
                    "a", encoding="utf-8"
            ) as file:
                file.write(str(chat_id) + "\n")
        except Exception as e:
            settings.LOGGER.info(f"Receiver writing error: {e}")

    def get_next_receiver(self):
        try:
            with open(
                    self.get_file(settings.RECEIVERS_FILE),
                    "r", encoding="utf-8"
            ) as file:
                lines = file.readlines()
                if not lines:
                    settings.LOGGER.info("Receivers file is empty")
                    return
                if not 0 <= self.current_receiver_index < len(lines):
                    self.current_receiver_index = 0
                line = lines[self.current_receiver_index]
                self.current_receiver_index += 1
                return int(line)
        except Exception as e:
            settings.LOGGER.info(f"Receiver reading error: {e}")

    def remove_receiver(self, chat_id: int):
        try:
            with open(
                    self.get_file(settings.RECEIVERS_FILE),
                    "r+", encoding="utf-8"
            ) as file:
                lines = file.readlines()
                line = str(chat_id) + "\n"
                if line in lines:
                    lines.remove(line)
                file.seek(0)
                file.writelines(lines)
                file.truncate(file.tell())
        except Exception as e:
            settings.LOGGER.info(f"Receiver removing error: {e}")

    def get_message_text(self):
        if not self._message_text:
            try:
                with open(
                        self.get_file(settings.MESSAGE_FILE),
                        "r", encoding="utf-8"
                ) as file:
                    self._message_text = file.read()
            except Exception as e:
                settings.LOGGER.info(f"Message reading error: {e}")
        if not self._message_text:
            return settings.DEFAULT_MESSAGE_TEXT
        return self._message_text

    def set_message_text(self, message_text: str):
        try:
            with open(settings.MESSAGE_FILE, "w", encoding="utf-8") as file:
                file.write(message_text)
                self._message_text = message_text
        except Exception as e:
            settings.LOGGER.info(f"Message writing error: {e}")


class Scheduler:
    @staticmethod
    def set_interval_func(scheduled_func: callable):
        settings.LOGGER.info("Preparing scheduler...")
        schedule.every(settings.SENDING_INTERVAL).minutes.do(scheduled_func)

    @staticmethod
    def work():
        settings.LOGGER.info("Scheduler works...")
        while True:
            schedule.run_pending()
            time.sleep(1)

    def run(self):
        settings.LOGGER.info("Running scheduler...")
        threading.Thread(target=self.work).start()


class ProjectManager:
    _instance = None

    app = Client(
        "tg-notify-userbot",
        api_id=settings.API_ID,
        api_hash=settings.API_HASH
    )
    scheduler = Scheduler()
    files_manager = FilesManager()

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ProjectManager, cls).__new__(cls)
        return cls._instance

    def send_message(self, chat_id: int = None):
        try:
            self.app.get_me()
        except AuthKeyUnregistered:
            return
        message_text = self.files_manager.get_message_text()
        receiver_id = (
            self.files_manager.get_next_receiver() if not chat_id else chat_id
        )
        if not receiver_id:
            settings.LOGGER.info("Message was not sent")
            return
        settings.LOGGER.info(f"Sending message to {receiver_id}...")
        self.app.send_message(
            receiver_id,
            message_text,
            parse_mode=ParseMode.MARKDOWN
        )

    def add_receiver(self, chat_id: int):
        settings.LOGGER.info(f"Adding receiver {chat_id}...")
        self.files_manager.add_receiver(chat_id)

    def remove_receiver(self, chat_id: int):
        settings.LOGGER.info(f"Removing receiver {chat_id}...")
        self.files_manager.remove_receiver(chat_id)

    def set_message_text(
            self,
            message_text: str,
    ):
        settings.LOGGER.info(
            "Setting new message text:\n"
            + "=" * 40 + "\n"
            + f"{message_text}\n"
            + "=" * 40
        )
        self.files_manager.set_message_text(message_text)

    def run(self):
        settings.LOGGER.info("Running app...")
        self.scheduler.set_interval_func(self.send_message)
        self.scheduler.run()
        settings.LOGGER.info("App successful started!")
        self.app.run()
