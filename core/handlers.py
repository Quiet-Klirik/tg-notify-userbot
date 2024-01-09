from pyrogram import Client, filters
from pyrogram.types import Message

from core.utils import ProjectManager


def prepare_handlers(project_manager: ProjectManager):
    app: Client = project_manager.app

    @app.on_message(
        filters.command("ad_set_message", prefixes=".") & filters.me
    )
    def set_message(_, message: Message):
        clear_message = message.text.markdown.split(
            ".ad_set_message ",
            maxsplit=1
        )[1]
        project_manager.set_message_text(clear_message)
        message.delete()

    @app.on_message(
        filters.command("ad_send", prefixes=".") & filters.me
    )
    def send_message(_, message: Message):
        project_manager.send_message(chat_id=message.chat.id)
        message.delete()

    @app.on_message(filters.command("ad_add", prefixes=".") & filters.me)
    def add_receiver(_, message: Message):
        chat_id = message.chat.id
        project_manager.add_receiver(chat_id)
        message.delete()

    @app.on_message(filters.command("ad_remove", prefixes=".") & filters.me)
    def remove_receiver(_, message: Message):
        chat_id = message.chat.id
        project_manager.remove_receiver(chat_id)
        message.delete()
