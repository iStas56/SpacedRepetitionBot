from datetime import datetime, timedelta, timezone
import requests
import os
from dotenv import load_dotenv
from dateutil import parser

load_dotenv()


class YandexApi:
    def __init__(self):
        self.oauth_token = os.getenv("YANDEX_OAUTH_TOKEN")
        self.iam_token = None
        self.expires_at = None
        self.get_new_iam_token()

    def get_new_iam_token(self):
        url = "https://iam.api.cloud.yandex.net/iam/v1/tokens"
        payload = {"yandexPassportOauthToken": self.oauth_token}
        response = requests.post(url, json=payload)
        if response.ok:
            self.iam_token = response.json()["iamToken"]
            self.expires_at = parser.isoparse(response.json()["expiresAt"])
        else:
            raise Exception("Ошибка при получении IAM токена")

    def is_token_expired(self):
        # Возвращает True, если срок действия токена истек или истекает менее чем через минуту
        return datetime.now(timezone.utc) >= (self.expires_at - timedelta(minutes=1))

    def get_token(self):
        if self.is_token_expired():
            self.get_new_iam_token()
        return self.iam_token

    def translate(self, word):
        token = self.get_token()
        url = "https://translate.api.cloud.yandex.net/translate/v2/translate"
        headers = {
            "Authorization": f"Bearer {token}"
        }
        data = {
            "folder_id": "bpf740bekgngp3ahgpgq",  # ID каталога в Яндекс.Облаке
            "texts": [word],
            "targetLanguageCode": "ru"
        }
        response = requests.post(url, headers=headers, json=data)
        if response.ok:
            translated_text = response.json()['translations'][0]['text']
            return translated_text
        else:
            return False
