import os
import time
from os import listdir
from os.path import isfile, join
from typing import List, Union
from urllib.parse import urlencode
import re
import json

import requests


class Telegram:
    def __init__(self, bot_token: str, bot_chat_id: str, service_id: str):
        self.bot_token = bot_token
        self.bot_chat_id = bot_chat_id
        self.url = f"https://api.telegram.org/bot{self.bot_token}/sendMessage?chat_id={self.bot_chat_id}&parse_mode=Markdown&text="

        self.service_id = service_id

        self.base_path = "/tmp/telegram"
        self.create_dir()

    def create_dir(self):
        os.makedirs(self.base_path, exist_ok=True)

    def get_last_message_sent_timestamp(self) -> Union[None, float]:
        onlyfiles = [
            f for f in listdir(self.base_path) if isfile(join(self.base_path, f))
        ]
        filter_id = [f for f in onlyfiles if f.startswith(self.service_id)]
        filter_id.sort(reverse=True)
        if len(filter_id) == 0:
            return
        return float(filter_id[0].split("_")[-1])

    def save_timestamp_file(self):
        try:
            with open(f"{self.base_path}/{self.service_id}_{time.time()}", "w") as file:
                file.write(" ")
        except Exception:
            pass

    def send_if_not_already_sent(
        self, messages: List[str], min_time_between_sent_min: int
    ):
        """method that allows to send messages with a hysteris time in between sents"""
        last_timestamp = self.get_last_message_sent_timestamp()
        if not last_timestamp or (
            time.time() - min_time_between_sent_min * 60 > last_timestamp
        ):
            self.send(messages)

    def send(self, messages: List[str]):
        """sends a message to telegram"""
        for message in messages:
            # message = re.sub("_", "-", json.dumps(message))
            requests.get(f"{self.url}{urlencode(message)}")
