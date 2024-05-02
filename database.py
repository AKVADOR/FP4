import sqlite3
import logging

import config

# Логирование
logging.basicConfig(filename=config.LOGS, level=logging.INFO, 
                    format="%(asctime)s FILE: %(filename)s IN: %(funcName)s MESSAGE: %(message)s", filemode="w")

# БД Объект
class Database:
    def __init__(self) -> None:
        logging.info("Инициализация базы данных")
        self._path = config.DB_FILE

        if config.RESET_DB:
            self.reset()

        self.init()
    
    # Инициализация БД
    def init(self):
        try:
            with sqlite3.connect(self._path) as conn:
                curs = conn.cursor()
                
                # создаем users, messages таблицы
                cmd1 = '''
                        CREATE TABLE IF NOT EXISTS users (
                            id INTEGER PRIMARY KEY,
                            used_gpt_tokens INTEGER,
                            used_tts_symbols INTEGER,
                            used_stt_blocks INTEGER)
                        '''
                cmd2 = '''
                        CREATE TABLE IF NOT EXISTS messages (
                            id INTEGER PRIMARY KEY,
                            uid INTEGER,
                            content TEXT,
                            role CHAR(16),
                            tokens INTEGER,
                            tts_symbols INTEGER,
                            stt_blocks INTEGER)
                        '''
                curs.execute(cmd1)
                curs.execute(cmd2)

                conn.commit()

                logging.info("База данных создана")
        except Exception as e:
            self.error("Не получилось инициализировать БД", e)

    # Ресет БД
    def reset(self):
        try:
            with sqlite3.connect(self._path) as conn:
                curs = conn.cursor()
                
                # Удаляем таблицы
                cmd1 = 'DROP TABLE IF EXISTS messages'
                cmd2 = 'DROP TABLE IF EXISTS users'
                curs.execute(cmd1)
                curs.execute(cmd2)

                conn.commit()
                logging.debug("База данных обнулена")
        except Exception as e:
            self.error("Не получилось обнулить БД", e)

    def __repr__(self) -> str:
        return f'Database({config.DB_FILE}) at <0x{hex(id(self)).upper()}>'
    
    def debug(self, text: str):
        if config.DEBUG:
            logging.debug(text)
    
    def error(self, text: str, e):
        logging.warning(text)
        logging.error(e)

    # Добавление сообщения в БД
    def add_message(self, uid: int, content: str, role: str, tokens: int, symbols: int, blocks: int) -> int | None:
        try:
            with sqlite3.connect(self._path) as conn:
                curs = conn.cursor()

                cmd = '''
                    INSERT INTO messages (uid, content, role, tokens, tts_symbols, stt_blocks)
                    VALUES (?, ?, ?, ?, ?, ?)
                '''
                curs.execute(cmd, (uid, content, role, tokens, symbols, blocks))
                conn.commit()
                id = curs.lastrowid

                self.debug(f"Добавление сообщения с ID ({id}) в БД")
                    
                return id
        except Exception as e:
            self.error("Не получилось добавить сообщение в БД", e)
    
    # Получить сообщение из БД
    def get_message(self, id: int) -> list | None:
        try:
            with sqlite3.connect(self._path) as conn:
                curs = conn.cursor()

                cmd = '''
                    SELECT * FROM messages WHERE id = ?
                '''
                curs.execute(cmd, (id,))
                return curs.fetchone()
        except Exception as e:
            self.error("Не получилось вернуть сообщение из БД", e)

    # Получить N сообщений от пользователя
    def get_nmessages(self, user_id: int, n: int):
        try:
            with sqlite3.connect(self._path) as conn:
                curs = conn.cursor()

                cmd = '''
                    SELECT * FROM messages WHERE uid = ? AND (role = "user" OR role = "assistant") ORDER BY id DESC LIMIT ? 
                '''
                curs.execute(cmd, (user_id, n))
                return curs.fetchall()
        except Exception as e:
            self.error(f"Не получилось вернуть сообщения от пользователя с ID ({user_id}) из БД", e)

    # Добавление пользователя в БД
    def add_user(self, user_id: int, used_gpt_tokens: int, used_tts_symbols: int, used_stt_blocks: int) -> int:
        try:
            with sqlite3.connect(self._path) as conn:
                curs = conn.cursor()

                cmd = '''
                    INSERT INTO users (id, used_gpt_tokens, used_tts_symbols, used_stt_blocks)
                    VALUES (?, ?, ?, ?)
                '''
                curs.execute(cmd, (user_id, used_gpt_tokens, used_tts_symbols, used_stt_blocks))
                conn.commit()

                self.debug(f"Добавление пользователя с ID ({id}) в БД")
                    
                return user_id
        except Exception as e:
            self.error("Не получилось добавить пользователя в БД", e)

    # Обновление пользователя в БД
    def update_user(self, user_id: int, used_gpt_tokens: int, used_tts_symbols: int, used_stt_blocks: int):
        try:
            with sqlite3.connect(self._path) as conn:
                curs = conn.cursor()
                cmd = '''
                    UPDATE users
                    SET used_gpt_tokens = used_gpt_tokens + ?,
                        used_tts_symbols = used_tts_symbols + ?,
                        used_stt_blocks = used_stt_blocks + ?
                    WHERE id = ?
                '''
                curs.execute(cmd, (used_gpt_tokens, used_tts_symbols, used_stt_blocks, user_id))
                conn.commit()

                self.debug(f"Обновление пользователя с ID ({user_id}) в БД")
        except Exception as e:
            self.error("Не получилось обновить пользователя в БД", e)

    # Получить пользователя из БД
    def get_user(self, id: int) -> list | None:
        try:
            with sqlite3.connect(self._path) as conn:
                curs = conn.cursor()

                cmd = "SELECT * FROM users WHERE id = ?"
                curs.execute(cmd, (id,))
                return curs.fetchone()
        except Exception as e:
            self.error("Не получилось вернуть пользователя из БД", e)

    # Получить число пользователей в БД
    def count_users(self) -> int:
        try:
            with sqlite3.connect(self._path) as conn:
                curs = conn.cursor()
                cmd = "SELECT COUNT(*) FROM users"
                curs.execute(cmd)
                return curs.fetchone()[0]
        except Exception as e:
            self.error("Не получилось вернуть число пользователей из БД", e)
    
    # Получить число сообщений в БД
    def count_messages(self) -> int:
        try:
            with sqlite3.connect(self._path) as conn:
                curs = conn.cursor()
                cmd = "SELECT COUNT(*) FROM messages"
                curs.execute(cmd)
                return curs.fetchone()[0]
        except Exception as e:
            self.error("Не получилось вернуть число пользователей из БД", e)

db = Database()

# Базовый объект для Message, User 
class IObject:
    def __init__(self, id):
        self.id = id
    
    @classmethod
    def add(cls):
        raise NotImplementedError("Подкласс должен реализовать этот метод")
    
    @classmethod
    def get(cls):
        raise NotImplementedError("Подкласс должен реализовать этот метод")

    @staticmethod
    def remove(id: int):
        raise NotImplementedError("Подкласс должен реализовать этот метод")
    
    @staticmethod
    def count():
        raise NotImplementedError("Подкласс должен реализовать этот метод")

    def __repr__(self) -> str:
        return f'IObject(id={self.id})'

# Объект пользователя
class User(IObject):
    def __init__(self, id: int, used_gpt_tokens: int, used_tts_symbols: int, used_stt_blocks: int):
        super().__init__(id)
        self.used_tokens = used_gpt_tokens
        self.used_symbols = used_tts_symbols
        self.used_blocks = used_stt_blocks
    
    # Обновить объект
    def refresh(self):
        usr = User.get(self.id)
        self.used_tokens = usr.used_tokens
        self.used_symbols = usr.used_symbols
        self.used_blocks = usr.used_blocks

    # добавить в БД
    @classmethod
    def add(cls, id: int, used_gpt_tokens: int = 0, used_tts_symbols: int = 0, used_stt_blocks: int = 0):
        db.add_user(id, used_gpt_tokens, used_tts_symbols, used_stt_blocks)
        return cls(id, used_gpt_tokens, used_tts_symbols, used_stt_blocks)
    
    # получить из БД
    @classmethod
    def get(cls, id: int):
        usr = db.get_user(id)
        if usr:
            return cls(*usr)

    # получить кол-во из БД
    @staticmethod
    def count():
        return db.count_users()

    def get_last_messages_json(self, n: int = 4):
        result = []
        msgs = self.get_last_messages(n)
        for msg in msgs:
            result.append({"role": msg.role, "text": msg.content, "tokens": msg.tokens})
        return result

    def get_last_messages(self, n: int = 4):
        result = []
        msgs = db.get_nmessages(self.id, n)
        for msg in msgs:
            result.append(Message(msg[0], msg[1], msg[2], msg[3], msg[4], msg[5], msg[6]))
        return result

    def __repr__(self) -> str:
        return f'User(id={self.id}, used_gpt_tokens={self.used_tokens}, used_tts_symbols={self.used_symbols}, used_stt_blocks={self.used_blocks})'

# Объект сообщения
class Message(IObject):
    def __init__(self, id: int, user_id: int, content: str, role: str, tokens: int, symbols: int, blocks: int):
        super().__init__(id)
        self.user_id = user_id
        self.content = content
        self.role = role
        self.tokens = tokens
        self.symbols = symbols
        self.blocks = blocks

    # добавить в БД
    @classmethod
    def add(cls, user: int | User, content: str, role: str, tokens: int, symbols: int, blocks: int):
        user_id = user.id if isinstance(user, User) else user

        _class = cls(None, user_id, content, role, tokens, symbols, blocks)
        _class.id = db.add_message(user_id, content, role, tokens, symbols, blocks)
        db.update_user(user_id, tokens, symbols, blocks)

        return _class
    
    # получить из БД
    @classmethod
    def get(cls, id: int):
        msg = db.get_message(id)
        if msg:
            return cls(*db.get_message(id))

    # получить кол-во из БД
    @staticmethod
    def count():
        return db.count_messages()

    def __repr__(self) -> str:
        return f'Message(id={self.id}, user_id={self.user_id}, role="{self.role}", tokens={self.tokens}, symbols={self.symbols}, blocks={self.blocks}, content="{self.content}")'




if __name__ == '__main__':
    usr1 = User.add(123)
    usr2 = User.add(1234)
    usr3 = User.add(12345)
    msg = Message.add(usr1, "test1", "system", 2, 7, 1)
    msg = Message.add(usr2, "test12", "user", 5, 3, 2)
    msg = Message.add(usr3, "test13", "assistant", 5, 3, 2)
    msg = Message.add(usr1, "test14", "system", 5, 3, 2)
    usr1.refresh()
    usr2.refresh()
    usr3.refresh()
    print(db.count_users())