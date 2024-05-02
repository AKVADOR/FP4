import requests
import logging

import config
from creds import get_creds


# Логирование
logging.basicConfig(filename=config.LOGS, level=logging.INFO, 
                    format="%(asctime)s FILE: %(filename)s IN: %(funcName)s MESSAGE: %(message)s", filemode="w")

# посчитать кол-во токенов
def count_gpt_tokens(messages):
    iam_token, folder_id = get_creds()
    url = "https://llm.api.cloud.yandex.net/foundationModels/v1/tokenizeCompletion"
    headers = {
        'Authorization': f'Bearer {iam_token}',
        'Content-Type': 'application/json'
    }
    data = {
        'modelUri': f"gpt://{folder_id}/yandexgpt-lite",
        "messages": messages
    }
    try:
        return len(requests.post(url=url, json=data, headers=headers).json()['tokens'])
    except Exception as e:
        logging.error(e)  # если ошибка - записываем её в логи
        return 0

# сделать запрос к GPT API
def ask_gpt(messages):
    iam_token, folder_id = get_creds()
    url = "https://llm.api.cloud.yandex.net/foundationModels/v1/completion"
    headers = {
        'Authorization': f'Bearer {iam_token}',
        'Content-Type': 'application/json'
    }
    data = {
        'modelUri': f'gpt://{folder_id}/yandexgpt-lite',
        'completionOptions': {
            'stream': False,
            'temperature': 0.7,
            'maxtokens': config.MAX_GPT_TOKENS
        },
        'messages': config.SYSTEM_PROMPT + messages
    }
    try:
        resp = requests.post(url, headers=headers, json=data)
        if resp.status_code != 200:
            return False, f"Ошибка GPT. HTML Respone Код: {resp.status_code}", None
        
        answer = resp.json()['result']['alternatives'][0]['message']['text']
        tokens_in_answer = count_gpt_tokens([{'role': 'assistant', 'text': answer}])
        return True, answer, tokens_in_answer
    except Exception as e:
        logging.error(e)
        return False, "Ошибка при обращении к GPT", None