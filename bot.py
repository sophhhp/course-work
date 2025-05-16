import os
import telebot
import requests
from telebot import types
import random

from bot_token import BOT_TOKEN


bot = telebot.TeleBot(BOT_TOKEN)

#создаётся словарь со словами-стимулами для эксперимента 
ALL_WORDS = ["абсолютный", "абсолютная", "неограниченный", "неограниченная", "полный", "полная",
             "тотальный", "тотальная", "беспросветный", "беспросветная", "безраздельный", "безраздельная"]

#список словарей пользователей 
user_lists = dict()
#список слов для тестирования каждого пользователя
user_words = dict()
#список пользователей, чьи результаты уже есть в системе
user_finished = list()


#приветственное сообщение с информацией
@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "Добрый день! \nМеня зовут Софья Путинцева, я учусь в НГУ на направлении \"Фундаментальная и прикладная лингвистика\". Для своей курсовой работы я собираю ассоциации к синонимичным прилагательным, чтобы исследовать особенности их семантики. \nЕсли вы готовы поучаствовать в моем исследовании, пожалуйста, выберите команду /instr. \nС результатами исследования можно будет ознакомиться в канале https://t.me/sp_associative_dictionary. \nСпасибо вам за участие!")


#сообщение с инструкцией к тесту
@bot.message_handler(commands=['instr'])
def send_message(message):
    bot.reply_to(message, "\nВам потребуется дать первую ассоциацию, возникающую у вас при виде слова. \n! Не задумывайтесь над ответом, правильных и неправильных ответов здесь нет :) \nЕсли вы готовы, выберите команду /start_test.  \nНачнём?")


#функция отправки слов-стимулов
@bot.message_handler(commands=['start_test'])
def send_word(message):
    #проверка на первое прохождение теста
    if not message.chat.id in user_finished and not message.chat.id in user_lists:
        user_lists[message.chat.id] = ALL_WORDS[:]
    #отправка слов-стимулов в ответ на слово-реакцию до момента пустого списка    
    if len(user_lists[message.chat.id]) != 0:
        user_words[message.chat.id] = random.choice(
            user_lists[message.chat.id])
        #удаление словаря пользователя, прошедшего тест
        user_lists[message.chat.id].remove(user_words[message.chat.id])
        bot.reply_to(message, user_words[message.chat.id])
    else:
        #добавление в список пользователей, прошедших тест
        user_finished.append(message.chat.id)
        #сообщение с благодарностью и ссылкой на результаты
        bot.reply_to(message, "Спасибо за участие в исследовании! \nС результатами можно будет ознакомиться в канале https://t.me/sp_associative_dictionary.")


#команда для удаления результатов пользователя с секретным паролем (о её наличии можно узнать только у создателя теста)
@bot.message_handler(commands=['remove_id'])
def remove_id(message):
    user_id = message.chat.id
    parts = message.text.split(' ')
    if len(parts) != 2:
        bot.reply_to(message, "Команда введена некорректно (возможно, вы забыли пароль)")
        bot.send_message(545157209, f"Пользователь {user_id} ввёл команду неправильно.")
    else:
        if parts[1] == 'sobaka34':
            if user_id in user_lists:
                user_lists[user_id] = ALL_WORDS[:]
                user_finished.remove(user_id)
                bot.reply_to(message, "ID удалён")
            else:
                bot.reply_to(message, "Вы не проходили тест ни разу, можете начать заново")
        else:
            bot.reply_to(message, "Неправильный пароль. Разработчик уведомлён.")
            bot.send_message(545157209, f"Пользователь {user_id} попытался сбросить свой ID и пройти тест заново, но ввёл неправильный пароль")
    

#запись результатов каждого пользователя в csv-файл 
@bot.message_handler()
def save_message(message):
    if not message.chat.id in user_finished:
        with open(f'results/{message.chat.id}.csv', 'a', encoding='utf-8') as f:
            f.write(user_words[message.chat.id] + ',' + message.text + '\n')
    send_word(message)


bot.infinity_polling()