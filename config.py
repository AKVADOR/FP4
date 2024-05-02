DEBUG = True
RESET_DB = True

MAX_USERS = 3
MAX_GPT_TOKENS = 120
COUNT_LAST_MSG = 4

MAX_USER_STT_BLOCKS = 10
MAX_USER_TTS_SYMBOLS = 5000
MAX_USER_GPT_TOKENS = 2000

HOME = '/home/student/gpt_bot'
LOGS = f'{HOME}logs.log'
DB_FILE = f'{HOME}database.db'
SYSTEM_PROMPT = [{'role': 'system', 'text': 'Ты весёлый собеседник. Общайся с пользователем на "ты" и используй юмор. Не объясняй, что ты умеешь и можешь. Общайся как человек. Отвечай коротко, как в переписке.'}]

IAM_TOKEN_PATH = f'{HOME}creds/iam_token.json'
FOLDER_ID_PATH = f'{HOME}creds/folder_id.txt'
TG_TOKEN_PATH = f'{HOME}creds/tg_token.txt'

VOICE = 'filipp'