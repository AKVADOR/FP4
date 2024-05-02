import requests
import logging
import config
import creds

# Логирование
logging.basicConfig(filename=config.LOGS, level=logging.INFO, 
                    format="%(asctime)s FILE: %(filename)s IN: %(funcName)s MESSAGE: %(message)s", filemode="w")

def text_to_speech(text):
    iam_token, folder_id = creds.get_creds()

    url = 'https://tts.api.cloud.yandex.net/speech/v1/tts:synthesize'
    headers = {'Authorization': f"Bearer {iam_token}"}
    data = {'text': text,  # текст, который нужно преобразовать в голосовое сообщение
            'lang': 'ru-RU',  # язык текста - русский
            'voice': config.VOICE,  # мужской голос Филиппа
            'folderId': folder_id, }

    response_tts = requests.post(
        url,
        headers=headers,
        data=data
    )
    if response_tts.status_code == 200:
        return True, response_tts.content
    else:
        return False, "При запросе в SpeechKit возникла ошибка"

def speech_to_text(data: bytes):
    iam_token, folder_id = creds.get_creds()

    # Указываем параметры запроса
    params = "&".join([
        "topic=general",  # используем основную версию модели
        f"folderId={folder_id}",
        "lang=ru-RU"  # распознаём голосовое сообщение на русском языке
    ])

    url = f"https://stt.api.cloud.yandex.net/speech/v1/stt:recognize?{params}"

    # Аутентификация через IAM-токен
    headers = {
        'Authorization': f'Bearer {iam_token}',
    }

    response = requests.post(
        url,
        headers=headers,
        data=data
    )

    # Читаем json в словарь
    decoded_data = response.json()

    # Проверяем, не произошла ли ошибка при запросе
    if decoded_data.get("error_code") is None and decoded_data.get("result"):
        return True, decoded_data.get("result")  # Возвращаем статус и текст из аудио
    else:
        return False, "При запросе в SpeechKit возникла ошибка."