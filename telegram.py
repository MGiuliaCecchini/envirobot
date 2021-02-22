import requests
import os

USER_ID = os.environ.get('ENVIROBOT_USERID')
TELEGRAM_API_KEY = os.environ.get('ENVIROBOT_TELEGRAM_API_KEY')

URL="https://api.telegram.org/bot" + TELEGRAM_API_KEY + "/sendMessage"


def send_message(text):
    payload = { 'chat_id': USER_ID,
               'text' : text,
               'disable_web_page_preview':'true',
               'parse_mode':'markdown'}
    resp = requests.post(URL, data=payload)
    return resp.status_code == 200
