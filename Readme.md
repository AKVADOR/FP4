# Python Telegram API Bot Assistant
Это простой текстовый и голосовой ассистент в Telegram.  
* Бот работает при помощи GPT, TTS, STT технологиях от [Yandex](ya.ru).  
* Бот написан на библиотеке [pyTelegramBotAPI](https://github.com/eternnoir/pyTelegramBotAPI).
## Задействованные технологии при разработке
* Редактор кода [Visual Studio Code](code.visualstudio.com) от [Microsoft](microsoft.com)
* Расширение VS Code для Python.
* Язык программирования [Python v3.12.3](https://www.python.org/downloads/release/python-3123/)
* Дополнительные библиотеки для [Python](python.org)
* API GPT yandexgpt-lite от [Yandex](ya.ru)
* API Text-To-Speech (синтез речи) от [Yandex](ya.ru)
* API Speech-To-Text (распознование) от [Yandex](ya.ru)
### Задействованные библиотеки
1. **time**  - Необходимо для определения времени чтобы провалидировать IAM_TOKEN.
2. **datetime** - То же самое что и 1 пункт.
3. **logging** - Необходимо для логирование.
4. **json** - Необходимо для чтения файла с токеном
5. **sqlite3** - Небходимо для работы с базой данных.
6. **requests** - Небходимо для работы с HTTP/S Протоколами, чтобы отправлять запросы на API сервера.
7. **telebot** - Необходимо для работы с API Telegram.

## Поддерживаемые команды
* /start - Запускает бота.
* /help - Выводит вспомогательное сообщение пользователю.
* /debug - Выводит информацию для отладки.
* /tts - Команда для проверки работы text-to-speech
* /stt - Команда для проверки работы speech-to-text

## Установка
* Для установки бота нужно ввести следующую команду `pip install -r requirements.txt`
* Для запуска бота нужно ввести следующую команду `python3 bot.py`