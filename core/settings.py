import logging
import os
import pathlib
import sys

from dotenv import load_dotenv

load_dotenv()
BASE_DIR = pathlib.Path(
    os.path.dirname(os.path.abspath(sys.argv[0]))
).resolve()

# Telegram API data
API_ID = os.environ["API_ID"]
API_HASH = os.environ["API_HASH"]


# Sending settings
SENDING_INTERVAL = float(os.environ.get("SENDING_INTERVAL", 30))
DEFAULT_MESSAGE_TEXT = os.environ.get("DEFAULT_MESSAGE_TEXT", "Hello!")


# Files settings
CONFIG_DIR = BASE_DIR / "config"

RECEIVERS_FILE = CONFIG_DIR / ".receivers"
MESSAGE_FILE = CONFIG_DIR / ".message"


# Logging settings
logging.getLogger("pyrogram").setLevel(logging.ERROR)
logging.basicConfig(
    format='%(name)s - %(asctime)s - [%(levelname)s] %(message)s',
    level=logging.INFO
)
LOGGER = logging.getLogger("tg-notify-userbot")
