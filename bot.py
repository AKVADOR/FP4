import telebot
import logging
import database
import validators
import yandex_gpt
import speechkit
import creds
import config

from database import User, Message

# Логирование
logging.basicConfig(filename=config.LOGS, level=logging.INFO, 
                    format="%(asctime)s FILE: %(filename)s IN: %(funcName)s MESSAGE: %(message)s", filemode="w")

token = creds.get_bot_token()

bot = telebot.TeleBot(token)


# start команда
@bot.message_handler(commands=['start'])
def start(message: telebot.types.Message):
    bot.send_message(message.from_user.id, "Привет! Отправь мне голосовое или текстовое сообщения, и я тебе отвечу!\n/help - для помощи")
    User.add(message.from_user.id)

# help команда
@bot.message_handler(commands=['help'])
def help(message: telebot.types.Message):
    bot.send_message(message.from_user.id, "Чтобы приступить к общению - отправь мне голосовое сообщение или текст\n"
                                            "Для тестирования возможностей SpeechKit:\n"
                                            "/tts - озвучивание твоего сообщения\n"
                                            "/stt - распознавание твоего голосового сообщения")
# debug команда
@bot.message_handler(commands=['debug'])
def debug(message: telebot.types.Message):
    with open("logs.log", "rb") as f:
        bot.send_document(message.from_user.id, f)

# speech to text команда
@bot.message_handler(commands=['stt'])
def stt_handler(message: telebot.types.Message):
    if not User.get(message.from_user.id):
        bot.send_message(message.from_user.id, "Для начала нужно прописать команду /start")
        return
    bot.send_message(message.from_user.id, "Режим проверки: отправь голосовое сообщение, чтобы я его распознал!")
    bot.register_next_step_handler(message, stt)

# text to speech команда
@bot.message_handler(commands=['tts'])
def tts_handler(message: telebot.types.Message):
    if not User.get(message.from_user.id):
        bot.send_message(message.from_user.id, "Для начала нужно прописать команду /start")
        return
    bot.send_message(message.from_user.id, "Режим проверки: отправь текстовое сообщение, чтобы я его озвучил!")
    bot.register_next_step_handler(message, tts)

def tts(message: telebot.types.Message):
    try:
        user_id = message.from_user.id
        text = message.text

        if message.content_type != "text":
            bot.send_message(user_id, "Отправь текстовое сообщение")
            return
        
        status_check_users, error_msg = validators.check_number_of_users(user_id)
        if not status_check_users:
            bot.send_message(user_id, error_msg)

        tts_symbols, error_msg = validators.is_tts_token_limit(user_id, text)
        if not error_msg:
            Message.add(user_id, text, "user_tts", 0, tts_symbols, 0)

            status, content = speechkit.text_to_speech(text)
            if status:
                bot.send_voice(user_id, content, reply_to_message_id=message.id)
                return
        bot.send_message(user_id, error_msg)
    except Exception as e:
        logging.error(e)

def stt(message: telebot.types.Message):
    try:
        user_id = message.from_user.id

        if not message.voice:
            bot.send_message(user_id, "Отправь голосовое сообщение")
            return
        
        status_check_users, error_msg = validators.check_number_of_users(user_id)
        if not status_check_users:
            bot.send_message(user_id, error_msg)

        stt_blocks, error_msg = validators.is_stt_block_limit(user_id, message.voice.duration)
        if error_msg:
            bot.send_message(user_id, error_msg)
            return

        file_id = message.voice.file_id
        file_info = bot.get_file(file_id)
        file = bot.download_file(file_info.file_path)

        status_stt, stt_text = speechkit.speech_to_text(file)
        if not status_stt:
            bot.send_message(user_id, stt_text)
            return

        Message.add(user_id, stt_text, 'user_stt', 0, 0, stt_blocks)

        bot.send_message(user_id, stt_text, reply_to_message_id=message.id)
    except Exception as e:
        logging.error(e)
        bot.send_message(message.from_user.id, "Не получилось ответить")

# Voice обработчик
@bot.message_handler(content_types=['voice'])
def handle_voice(message: telebot.types.Message):
    try:
        if not User.get(message.from_user.id):
            bot.send_message(message.from_user.id, "Для начала нужно прописать команду /start")
            return
        user_id = message.from_user.id

        status_check_users, error_msg = validators.check_number_of_users(user_id)
        if not status_check_users:
            bot.send_message(user_id, error_msg)
            return
        
        stt_blocks, error_msg = validators.is_stt_block_limit(user_id, message.voice.duration)
        if error_msg:
            bot.send_message(user_id, error_msg)
            return
        
        file_id = message.voice.file_id
        file_info = bot.get_file(file_id)
        file = bot.download_file(file_info.file_path)
        status_stt, stt_text = speechkit.speech_to_text(file)
        if not status_stt:
            bot.send_message(user_id, stt_text)
            return
        
        Message.add(user_id, stt_text, "user", 0, 0, stt_blocks)

        last_messages = database.User.get(user_id).get_last_messages_json(config.COUNT_LAST_MSG)
        total_gpt_tokens, error_msg = validators.is_gpt_token_limit(last_messages)
        if error_msg:
            bot.send_message(user_id, error_msg)
            return
        
        status_gpt, answer_gpt, tokens_in_answer = yandex_gpt.ask_gpt(last_messages)
        if not status_gpt:
            bot.send_message(user_id, answer_gpt)
            return
        
        tts_symbols, error_msg = validators.is_tts_token_limit(user_id, answer_gpt)
        Message.add(user_id, answer_gpt, "assistant", tokens_in_answer, tts_symbols, 0)

        if not error_msg:

            status, content = speechkit.text_to_speech(answer_gpt)
            if status:
                bot.send_voice(user_id, content, reply_to_message_id=message.id)
                return
            
            error_msg = content
        
        bot.send_message(user_id, error_msg)
        bot.send_message(user_id, answer_gpt, reply_to_message_id=message.id)
    except Exception as e:
        logging.error(e)

# Text обработчик
@bot.message_handler(content_types=['text'])
def handle_text(message: telebot.types.Message):
    try:
        if not User.get(message.from_user.id):
            bot.send_message(message.from_user.id, "Для начала нужно прописать команду /start")
            return
        user_id = message.from_user.id

        status_check_users, error_msg = validators.check_number_of_users(user_id)
        if not status_check_users:
            bot.send_message(user_id, error_msg)
        
        Message.add(user_id, message.text, 'user', 0, 0, 0)

        last_messages = database.User.get(user_id).get_last_messages_json(config.COUNT_LAST_MSG)

        total_gpt_tokens, error_msg = validators.is_gpt_token_limit(last_messages)
        if error_msg:
            bot.send_message(user_id, error_msg)
            return

        status_gpt, answer_gpt, tokens_in_answer = yandex_gpt.ask_gpt(last_messages)
        if not status_gpt:
            bot.send_message(user_id, answer_gpt)
            return
        total_gpt_tokens += tokens_in_answer

        Message.add(user_id, answer_gpt, "assistant", tokens_in_answer, 0, 0)

        bot.send_message(user_id, answer_gpt, reply_to_message_id=message.id)
    except Exception as e:
        logging.error(e)
        bot.send_message(message.from_user.id, "Не получилось ответить. Попробуй написать другое сообщение.")

@bot.message_handler(func=lambda: True)
def handler(message):
    bot.send_message(message.from_user.id, "Отправь мне голосовое или текстовое сообщения, и я тебе отвечу")

if __name__ == "__main__":
    logging.info("Запускаем Бота")
    bot.polling()