import dotenv
from rich.logging import RichHandler
import logging
import os

dotenv.load_dotenv()
logging.basicConfig(level=os.getenv("LOG_LEVEL"), handlers=[RichHandler()])
logging.debug(os.getenv("DEVICE_TOKEN"))

from sms import poll_sms
from push.bark import push as bark_push
from functools import partial


def log_sms(func):
    def wrapper(sms):
        logging.debug(sms)
        return func(sms)

    return wrapper


poll_sms(log_sms(partial(bark_push, group=os.getenv("BARK_GROUP"))))
