from bd import create_table, insert_row, count_all_symbol
from main import text_to_speech
import telebot
from telebot.types import ReplyKeyboardMarkup, KeyboardButton, Message
from telebot import types


bot = telebot.TeleBot(token="6056165962:AAHWFn9jmx4zYz8q-5d0tW8_-ot7aCVBir4")
administrators = []
stop = 'Отказано!'
markup_menu = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)


MAX_USER_VOICE_ACTING_SYMBOLS = 100
MAX_VOICE_ACTING_SYMBOLS = 1000
create_table('messages')


@bot.message_handler(commands=['debug'])
def debug(message):
    user_id = message.chat.id
    if user_id in administrators:
        with open('errors.cod.log', 'rb') as file:
            bot.send_document(message.chat.id, file)
    else:
        bot.send_message(message.chat.id, stop)


def hello(message):
    msg = 'привет'
    return msg in message.text.lower()


def mood(message):
    msg = 'а как у тебя дела?'
    return msg in message.text.lower()


def mood1(message):
    msg = 'отлично'
    return msg in message.text.lower()


def bye(message):
    msg = 'пока'
    return msg in message.text.lower()


def button(buttons):
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    for ell in buttons:
        keyboard.add(KeyboardButton(ell))

    return keyboard


def is_voice_acting_symbol_limit(message, text):
    user_id = message.from_user.id
    text_symbols = len(text)

    # Функция из БД для подсчёта всех потраченных пользователем символов
    all_symbols = count_all_symbol(user_id) + text_symbols

    # Сравниваем all_symbols с количеством доступных пользователю символов
    if all_symbols >= MAX_USER_VOICE_ACTING_SYMBOLS:
        msg = f"Превышен общий лимит Speechkit {MAX_USER_VOICE_ACTING_SYMBOLS}. \n" \
              f"Использовано: {all_symbols} символов. " \
              f"Доступно: {MAX_USER_VOICE_ACTING_SYMBOLS - all_symbols}"
        bot.send_message(user_id, msg)
        return None

    # Сравниваем количество символов в тексте с максимальным количеством символов в тексте
    if text_symbols >= MAX_VOICE_ACTING_SYMBOLS:
        msg = f"Превышен лимит Speechkit на запрос {MAX_VOICE_ACTING_SYMBOLS}, в сообщении {text_symbols} символов"
        bot.send_message(user_id, msg)
        return None
    return len(text)


@bot.message_handler(commands=['start'])
def handler_start(message: Message):
    user_id = message.from_user.id
    bot.send_message(chat_id=message. chat.id, text=f'Привет,  {message.from_user.first_name}\n'
                                                    'Это Телеграм бот, который озвучивает твой текст.\n'
                                                    'Нажми команду voice_acting или кнопку "Озвучить текст",'
                                                    'чтобы озвучить текст',
                     reply_markup=button(["Озвучить текст"]))


@bot.message_handler(func=lambda message: message.text == "Озвучить текст")
def voice_acting_handler(message):
    user_id = message.from_user.id
    bot.send_message(user_id, 'Напиши текст, который ты хочешь озвучить!')
    bot.register_next_step_handler(message, voice_acting)


@bot.message_handler(commands=['voice_acting'])
def voice_acting_handler(message):
    user_id = message.from_user.id
    bot.send_message(user_id, 'Напиши текст, который ты хочешь озвучить!')
    bot.register_next_step_handler(message, voice_acting)


def voice_acting(message):
    user_id = message.from_user.id
    text = message.text

    if message.content_type != 'text':
        bot.send_message(user_id, 'Отправь текстовое сообщение')
        return

    text_symbol = is_voice_acting_symbol_limit(message, text)
    if text_symbol is None:
        return

    insert_row(user_id, text, text_symbol)

    status, content = text_to_speech(text)

    if status:
        bot.send_voice(user_id, content)
    else:
        bot.send_message(user_id, content)


@bot.message_handler(func=lambda message: message.text == 'Вернуться в меню')
def house(message):
    bot.send_message(message.chat.id, 'Перевожу в главное меню:', reply_markup=markup_menu)


bot.infinity_polling()