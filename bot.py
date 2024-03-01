import os
from datetime import datetime

from dotenv import load_dotenv
from telebot import TeleBot, types

from scrapper import get_exchange_rates

load_dotenv()

TOKEN = os.getenv('TOKEN')

bot = TeleBot(TOKEN)

DELAY = 3600

date, currencies, last_update = get_exchange_rates()


def all_currencies(scrapper_data):
    result = ''
    for key in scrapper_data:
        result += scrapper_data[key][0] + ' '
        result += scrapper_data[key][1] + ' = '
        result += scrapper_data[key][2] + '₽ '
        result += f'по курсу ЦБ на {date}.\n'
    return result


USD = (
    f"{currencies['USD'][0]} "
    f"{currencies['USD'][1]} = "
    f"{currencies['USD'][2]}₽ на {date}."
)
EUR = (
    f"{currencies['EUR'][0]} "
    f"{currencies['EUR'][1]} = "
    f"{currencies['EUR'][2]}₽ на {date}."
)
ALL_CURRENCIES = all_currencies(currencies)
ALL_COMMANDS = (
    'Список всех комманд бота:\n'
    '/start - начало работы.\n'
    'all - получение списка всех курсов валют.\n'
    'idx - получить все индексы валют.\n'
    'USD - получение курса под индексом "USD".\n'
    'Для получения курса другой валюты введите ее индекс.\n'
    'Например RSD для Сербсих динаров.\n'
)


def check_updates():
    """Получаем свежие данные. 1 запрос в час."""
    global date, currencies, last_update
    if (datetime.now().timestamp() - last_update) > DELAY:
        date, currencies, last_update = get_exchange_rates()


def markup():
    """Разметка кнопок быстрой навигации для популярных команд."""
    markup = types.InlineKeyboardMarkup()
    all_currencies = types.InlineKeyboardButton(
        'ИНФОРМАЦИЯ', callback_data='Полный список команд:'
    )
    usd = types.InlineKeyboardButton('Курс доллара США', callback_data=USD)
    eur = types.InlineKeyboardButton('Курс ЕВРО', callback_data=EUR)
    markup.row(eur, usd)
    markup.row(all_currencies)
    return markup


MARKUP = markup()


@bot.message_handler(commands=['start'])
def info(message):
    """Обработчик команд (/start)."""
    check_updates()
    bot.send_message(message.chat.id, 'Welcome!', reply_markup=MARKUP)


@bot.callback_query_handler(func=lambda callback: True)
def handle(callback):
    """Обработчик нажатия кнопок."""
    check_updates()
    if callback.data == 'Полный список команд:':
        bot.send_message(
            callback.message.chat.id, ALL_COMMANDS, reply_markup=MARKUP
        )
    else:
        bot.send_message(
            callback.message.chat.id, callback.data, reply_markup=MARKUP
        )


@bot.message_handler()
def echo_message(message):
    """
    Основная логика работы бота.
    Получает сообщение и в зависимости от типа высылает результат.
    """
    check_updates()
    if message.text.upper() in currencies.keys():
        bot.send_message(
            message.chat.id, (
                f'{currencies[message.text.upper()][0]} '
                f'{currencies[message.text.upper()][1]} = '
                f'{currencies[message.text.upper()][2]}₽ '
                f'по курсу ЦБ на {date}.'
            ),
            reply_markup=MARKUP
        )
    elif message.text.upper() == 'ALL':
        bot.send_message(message.chat.id, ALL_CURRENCIES, reply_markup=MARKUP)
    elif message.text.upper() == 'IDX':
        bot.send_message(
            message.chat.id,
            '\n'.join([x for x in currencies.keys()]),
            reply_markup=MARKUP
        )
    else:
        bot.send_message(
            message.chat.id,
            'Индекс указанной валюты не найден.',
            reply_markup=MARKUP
        )


bot.infinity_polling()
