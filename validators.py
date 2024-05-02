import database
import config
from config import MAX_GPT_TOKENS, MAX_USER_GPT_TOKENS, MAX_USER_STT_BLOCKS, MAX_USER_TTS_SYMBOLS, MAX_USERS


def check_number_of_users(user_id):
    user = database.User.get(user_id)
    if user:
        return True, None
    
    amount_of_users = database.User.count()
    if amount_of_users >= config.MAX_USERS:
        return False, "Слишком много пользователей"
    return True, None

def is_gpt_token_limit(messages):
    total_toks = 0

    for msg in messages:
        total_toks += msg.get("tokens")

    if total_toks > config.MAX_GPT_TOKENS:
        msg = f"Превышен лимит токенов.\nВсего токенов {total_toks}/{config.MAX_GPT_TOKENS}"
        return total_toks, msg
    return total_toks, None

def is_stt_block_limit(user_id, duration):
    # Функция из БД для подсчёта всех потраченных пользователем аудиоблоков
    all_blocks = database.User.get(user_id).used_blocks

    # Проверяем, что аудио длится меньше 30 секунд
    if duration >= 30:
        msg = "SpeechKit STT работает с голосовыми сообщениями меньше 30 секунд"
        return False, msg

    # Сравниваем all_blocks с количеством доступных пользователю аудиоблоков
    if all_blocks >= MAX_USER_STT_BLOCKS:
        msg = f"Превышен общий лимит SpeechKit STT {MAX_USER_STT_BLOCKS}. Использовано {all_blocks} блоков. Доступно: {MAX_USER_STT_BLOCKS - all_blocks}"
        return False, msg

    return True, None

def is_tts_token_limit(user_id, text):
    len_text = len(text)

    # Функция из БД для подсчёта всех потраченных пользователем аудиоблоков
    all_tokens = database.User.get(user_id).used_blocks + len_text

    # Сравниваем количество символов в тексте с максимальным количеством символов в тексте
    if all_tokens > MAX_USER_TTS_SYMBOLS:
        msg = f"Превышен общий лимит SpeechKit TTS {MAX_USER_TTS_SYMBOLS}. Использовано: {all_tokens - len_text} символов. Доступно: {MAX_USER_TTS_SYMBOLS - all_tokens + len_text}"
        return False, msg
    return True, None