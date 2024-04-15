import sqlite3
import telebot
bot = telebot.TeleBot(token="6056165962:AAHWFn9jmx4zYz8q-5d0tW8_-ot7aCVBir4")

DB_NAME = 'database.db'
TABLE_NAME = 'texts'
MAX_USER_VOICE_ACTING_SYMBOLS = 100
MAX_VOICE_ACTING_SYMBOLS = 1000


# Функция для подключения к базе данных или создания новой, если её ещё нет
def create_db(database_name=DB_NAME):
    connection = sqlite3.connect(database_name)
    connection.close()


def execute_query(sql_query, data=None, db_path=DB_NAME):
    with sqlite3.connect(db_path) as connection:
        cursor = connection.cursor()
        if data:
            cursor.execute(sql_query, data)
        else:
            cursor.execute(sql_query)
        connection.commit()


def send_token_warning_message(bot: telebot.TeleBot, chat_id: int, all_tokens: int):
    bot.send_message(
        chat_id,
        f"Вы приближаетесь к лимиту {MAX_USER_VOICE_ACTING_SYMBOLS}"
    )


# Функция для выполнения любого sql-запроса для получения данных (возвращает значение)
def execute_selection_query(sql_query, data=None, db_path=DB_NAME):
    connection = sqlite3.connect(db_path)
    cursor = connection.cursor()
    if data:
        cursor.execute(sql_query, data)
    else:
        cursor.execute(sql_query)
    rows = cursor.fetchall()
    connection.close()
    return rows


def create_table(db_name="speech_kit.db"):
    try:
        # Создаём подключение к базе данных
        with sqlite3.connect(db_name) as conn:
            cursor = conn.cursor()
            # Создаём таблицу messages
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY,
                user_id INTEGER,
                message TEXT,
                tts_symbols INTEGER)
            ''')
            # Сохраняем изменения
            conn.commit()
    except Exception as e: (
        print(f"Error: {e}"))


# Функция для вставки новой строки в таблицу
def insert_row(user_id, message, tts_symbols, db_name="speech_kit.db"):
    try:
        # Подключаемся к базе
        with sqlite3.connect(db_name) as conn:
            cursor = conn.cursor()
            # Вставляем в таблицу новое сообщение
            cursor.execute('''INSERT INTO messages (user_id, message, tts_symbols)VALUES (?, ?, ?)''',
                           (user_id, message, tts_symbols))
            # Сохраняем изменения
            conn.commit()
    except Exception as e:  # обрабатываем ошибку и записываем её в переменную <e>
        print(f"Error: {e}")  # выводим ошибку в консоль


def count_all_symbol(user_id, db_name="speech_kit.db"):
    try:
        # Подключаемся к базе
        with sqlite3.connect(db_name) as conn:
            cursor = conn.cursor()
            # Считаем, сколько символов использовал пользователь
            cursor.execute('''SELECT SUM(tts_symbols) FROM messages WHERE user_id=?''', (user_id,))
            data = cursor.fetchone()
            # Проверяем data на наличие хоть какого-то полученного результата запроса
            # И на то, что в результате запроса мы получили какое-то число в data[0]
            if data and data[0]:
                # Если результат есть и data[0] == какому-то числу, то
                return data[0]  # возвращаем это число - сумму всех потраченных символов
            else:
                # Результата нет, так как у нас ещё нет записей о потраченных символах
                return 0  # возвращаем 0
    except Exception as e:
        print(f"Error: {e}")


def is_voice_acting_symbol_limit(message, text):
    user_id = message.from_user.id
    text_symbols = len(text)

    # Функция из БД для подсчёта всех потраченных пользователем символов
    all_symbols = count_all_symbol(user_id) + text_symbols

    # Сравниваем all_symbols с количеством доступных пользователю символов
    if all_symbols >= MAX_USER_VOICE_ACTING_SYMBOLS:
        msg = f"Превышен общий лимит SpeechKit {MAX_USER_VOICE_ACTING_SYMBOLS}." \
              f" Использовано: {all_symbols} символов.\n" \
              f" Доступно: {MAX_USER_VOICE_ACTING_SYMBOLS - all_symbols}"
        bot.send_message(user_id, msg)
        return None

    # Сравниваем количество символов в тексте с максимальным количеством символов в тексте
    if text_symbols >= MAX_VOICE_ACTING_SYMBOLS:
        msg = f"Превышен лимит SpeechKit на запрос {MAX_VOICE_ACTING_SYMBOLS}, в сообщении {text_symbols} символов"
        bot.send_message(user_id, msg)
        return None

    elif all_symbols / 2 >= MAX_VOICE_ACTING_SYMBOLS:  # Если осталось меньше половины
        msg = f'Вы использовали больше половины токенов в этой сессии. '
        f'Ваш запрос содержит суммарно {MAX_VOICE_ACTING_SYMBOLS} токенов.'
        bot.send_message(user_id, msg)
        return len(text)
