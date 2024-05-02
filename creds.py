import requests
import logging
import json
import time
from datetime import datetime

import config

logging.basicConfig(filename=config.LOGS, level=logging.INFO, 
                    format="%(asctime)s FILE: %(filename)s IN: %(funcName)s MESSAGE: %(message)s", filemode="w")

# Создание нового токена
def create_new_token():
    url = "http://169.254.169.254/computeMetadata/v1/instance/service-accounts/default/token"
    headers = {
        "Metadata-Flavor": "Google"
    }
    try:
        # Запрос на сервер чтобы получить новый IAM_TOKEN
        resp = requests.get(url, headers=headers)
        if resp.status_code == 200:
            data = resp.json()
            data['expires_at'] = time.time() + data['expires_in']
            # Запись IAM_TOKEN в файл
            with open(config.IAM_TOKEN_PATH, "w") as f:
                json.dump(data, f)
            logging.info("Получен новый IAM_TOKEN")
        else:
            logging.error(f"Ошибка получения iam_token. HTML Respone code: {resp.status_code}")
    except Exception as e:
        logging.error(f"Ошибка получения iam_token: {e}")

# Получение IAM_TOKEN и FOLDER_ID
def get_creds():
    try:
        # Читаем IAM_TOKEN из файла
        with open(config.IAM_TOKEN_PATH) as f:
            data = json.load(f)
            expire = datetime.strptime(data['expires_at'][:26], "%Y-%m-%dT%H:%M:%S.%f")
            # Если закончился период работы токена
            if datetime.now() > expire:
                logging.info("Период работы IAM_TOKEN истёк.")
                create_new_token()
    except Exception as e:
        logging.error(e)
        create_new_token()
    
    with open(config.IAM_TOKEN_PATH, 'r') as f:
        data = json.load(f)
        iam_token = data['access_token']
    
    with open(config.FOLDER_ID_PATH, 'r') as f:
        folder_id = f.read().strip()
    
    return iam_token, folder_id

def get_bot_token():
    with open(config.TG_TOKEN_PATH, 'r') as f:
        return f.read().strip()