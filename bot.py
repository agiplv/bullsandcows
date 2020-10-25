import logging

import sys
from time import sleep

import telebot
from bullsandcows import BullAndCows

bot = telebot.TeleBot("1368410071:AAF1D1RSihShCKLOnIwm0pnMEwZvHO_qKGM")

logger = telebot.logger
formatter = logging.Formatter(
    '[%(asctime)s] %(thread)d {%(pathname)s:%(lineno)d} %(levelname)s - %(message)s',
    '%m-%d %H:%M:%S'
)
ch = logging.StreamHandler(sys.stdout)
logger.addHandler(ch)
logger.setLevel(logging.INFO)  # or use logging.INFO
ch.setFormatter(formatter)

commands = [
    telebot.types.BotCommand('start', 'start game'),
    telebot.types.BotCommand('answer', 'get answer'),
    telebot.types.BotCommand('help', 'get help')
]
bot.set_my_commands(commands)

game = BullAndCows()


@bot.message_handler(commands=['start'])
def send_start(message):
    keyboard = telebot.types.InlineKeyboardMarkup()
    if not game.get_secret(message.chat.id):
        keyboard.row(
            telebot.types.InlineKeyboardButton('Play', callback_data='play'),
            telebot.types.InlineKeyboardButton('Rules', callback_data='rules')
        )
    else:
        if game.get_win(message.chat.id):
            keyboard.row(
                telebot.types.InlineKeyboardButton('New Game', callback_data='restart'),
                telebot.types.InlineKeyboardButton('Rules', callback_data='rules')
            )
        else:
            keyboard.row(
                telebot.types.InlineKeyboardButton('New Game', callback_data='restart'),
                telebot.types.InlineKeyboardButton('Previous Game', callback_data='continue'),
            )

    bot.send_message(
        message.chat.id,
        "<b>Bulls and Cows</b>",
        reply_markup=keyboard,
        parse_mode='HTML')


@bot.callback_query_handler(func=lambda call: True)
def iq_callback(query):
    data = query.data
    if data == 'play':
        bot.answer_callback_query(query.id, "Game started")
        if not game.get_secret(query.message.chat.id):
            reply = game.start_game(query.message.chat.id)
            bot.send_message(query.message.chat.id, reply)
    if data == 'restart':
        game.restart_game(query.message.chat.id)
        bot.answer_callback_query(query.id, "Game started")
        bot.send_message(query.message.chat.id, game.start_message)
    if data == 'rules':
        bot.answer_callback_query(query.id, "Game rules")
        bot.send_message(query.message.chat.id, game.help)
    if data == 'continue':
        bot.answer_callback_query(query.id,"Continue gaming")


@bot.message_handler(commands=['answer'])
def send_play(message):
    reply = game.get_secret(message.chat.id)
    if reply:
        bot.reply_to(message, reply)


@bot.message_handler(commands=['help'])
def send_help(message):
    if game.help:
        bot.send_message(message.chat.id, game.help)


@bot.message_handler(func=lambda message: True)
def echo_all(message):
    game.start_game(message.chat.id)
    guess = message.text.strip()
    keyboard = telebot.types.InlineKeyboardMarkup()
    keyboard.row(
        telebot.types.InlineKeyboardButton('New Game', callback_data='restart')
    )
    print(message)
    if game.get_win(message.chat.id):
        won = bot.send_message(message.chat.id,"Game is not active.", reply_markup=keyboard)
        sleep(5)
        bot.delete_message(message.chat.id, message.message_id)
        bot.delete_message(won.chat.id,won.message_id)
    else:
        reply, validate = game.guess(guess, message.chat.id)

        if game.get_win(message.chat.id):
            keyboard = telebot.types.InlineKeyboardMarkup()
            keyboard.row(
                telebot.types.InlineKeyboardButton('New Game', callback_data='restart')
            )
            attempts = game.get_attempts(message.chat.id)
            answer = game.get_secret(message.chat.id)
            star = "⭐"
            stars = star*(11-attempts)
            bot.send_message(message.chat.id,"⭐🏆⭐")
            bot.send_message(
                message.chat.id,
                "<b>You won with answer %s!!!🏆</b>\nNumber of attempts: %s.\n%s" % (answer, attempts, stars),
                reply_markup=keyboard,
                parse_mode='HTML')
        else:
            if not validate:
                if reply:
                    bad = bot.send_message(message.chat.id, reply)
                    sleep(3)
                    bot.delete_message(message.chat.id, message.message_id)
                    bot.delete_message(bad.chat.id,bad.message_id)
            else:
                for reply in reply.split('\n'):
                    if reply:
                        bot.send_message(message.chat.id, reply)


bot.polling()
