import logging
import telebot
from telebot.types import Message, CallbackQuery
from telebot import types
import json

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(levelname)s %(message)s'
)
logger = logging.getLogger(__name__)

bot = telebot.TeleBot('TOKEN')
users_data = dict()


@bot.message_handler(commands=['start'], content_types=['text'])
def hello(message: Message):
    logger.info(f'{message.from_user.username} send "start" command')

    markup = types.InlineKeyboardMarkup(row_width=1)
    item = types.InlineKeyboardButton('💬 Диолог', callback_data='dialog')
    markup.add(item)

    bot.send_message(message.chat.id, 'Привет!', reply_markup=markup)



@bot.callback_query_handler(func=lambda call: True)
def dialog(call: CallbackQuery):
    if call.message:
        if call.data == 'dialog':
            logger.info(f'{call.message.from_user.username} send "dialog" command')
            bot.send_message(call.message.chat.id, 'Введите ваше имя')
            bot.register_next_step_handler(call.message, get_name)

        if call.data == 'create':
            bot.register_next_step_handler(call.message, dialog)

        try:
            if call.data == 'info':
                logger.info(f'{call.message.from_user.username} send "get_me" command')
                for item, value in users_data[call.message.chat.id].items():
                    bot.send_message(call.message.chat.id, str(f'{item} - {value}'))
        except:
            bot.send_message(call.message.chat.id, 'О вас нет никаких данных :(')
            markup = types.InlineKeyboardMarkup(row_width=1)
            item1 = types.InlineKeyboardButton('Да', callback_data='create')
            item2 = types.InlineKeyboardButton('Нет', callback_data='not_create')
            markup.add(item1, item2)

            bot.send_message(call.message.chat.id, 'Хотите создать новый аккаунт?', reply_markup=markup)




def get_name(message: Message):
    users_data[message.chat.id] = {'name': message.text}
    users_data[message.chat.id]['user_name'] = message.from_user.username

    bot.send_message(message.chat.id, 'Введите вашу фамилию')
    bot.register_next_step_handler(message, get_surname)


def get_surname(message: Message):
    users_data[message.chat.id]['surname'] = message.text

    bot.send_message(message.chat.id, 'Введите вашу страну')
    bot.register_next_step_handler(message, get_country)


def get_country(message: Message):
    with open('countries.txt', 'r', encoding='utf8') as file:
        countries = file.read().split('\n')
    users_data[message.chat.id]['country'] = message.text
    if users_data[message.chat.id]['country'] in countries:
        bot.send_message(message.chat.id, 'Введите вашу почту')
        bot.register_next_step_handler(message, get_email)
    else:
        bot.send_message(message.chat.id, 'Такой страны не существует.')
        bot.register_next_step_handler(message, get_country)


def get_email(message: Message):
    users_data[message.chat.id]['email'] = message.text
    if '@' in users_data[message.chat.id]['email'] and '.com' in users_data[message.chat.id]['email'] or '.ru' in users_data[message.chat.id]['email']:
        save_user(message.chat.id)
    else:
        bot.send_message(message.chat.id, 'Пожалуйста внимательно проверте написание вашей почты')
        bot.register_next_step_handler(message, get_email)


def save_user(chat_id):
    users_data[chat_id]['user_id'] = chat_id
    with open('user.json', 'w', encoding='utf-8') as outfile:
        json.dump(users_data, outfile, ensure_ascii=False, indent=4)
    logger.info(f"{users_data[chat_id]['user_name']} saved")

@bot.message_handler(commands=['info'], content_types=['text'])
def get_info(message: Message):

    markup1 = types.InlineKeyboardMarkup(row_width=1)
    item1 = types.InlineKeyboardButton('ℹ Мое инфо', callback_data='info')
    markup1.add(item1)

    bot.send_message(message.chat.id, 'Хотите посмотреть информацию о себе?', reply_markup=markup1)


if __name__ == '__main__':
    bot.infinity_polling()
