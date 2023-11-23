import telebot
from telebot import types
import os
import psycopg2 

TOKEN = '6534971012:AAEXWo4l06RS8U-6nzXbrwmGVy5YnUZNBIs'

bot = telebot.TeleBot(TOKEN)

DATABASE_URL = '/'

# CONNECTING TO DATABASE
try:
    conn = psycopg2.connect(DATABASE_URL, sslmode='require')
    cursor = conn.cursor()
    print("Connected to PostgresSQL Database")
except psycopg2.OperationalError as e:
    print(f"Failed to connet to PostgreSQL:  {e}")

@bot.message_handler(commands=['start'])
def send_welcome(message):
    try:
        # Отправляем гифку
        sticker_id = 'CAACAgIAAxkBAAEKxHNlVmqDS5OS1wg6tPWy-luHOluKjgAC3AUAAj-VzArxX-zMZBcVlzME'  # Замените на реальную ссылку на ваш стикер
        bot.send_sticker(message.chat.id, sticker_id)

        # Отправляем приветственное сообщение
        welcome_message = (
        "Добро пожаловать в IMEL!\n"
        "IMEL – система, разрабатываемая для студий маникюра и салонов красоты, позволяющая оптимизировать процесс создания дизайна ногтей,"
        "подготовки мастера к работе с отдельным клиентом, предоставляющая аналитику на основе выбранных дизайнов"
        "Создайте заранее запись, используя конструктор (кнопка в меню)\n"
        "Выберите салон:"
        )
        # EXECUTE FROM DATABASE SHOP LIST
        cursor.execute("SELECT id, name FROM shops")
        shops = cursor.fetchall()
        # INLINEKEYBOARDMARKUP FOR SHOP LIST
        keyboard = types.InlineKeyboardMarkup(row_width=2)
        for shop in shops:
            shop_id, shop_name = shop
            key = types.InlineKeyboardButton(text=shop_name, callback_data=f'shop_{shop_id}')
            keyboard.add(key)
        bot.send_message(message.chat.id, welcome_message, reply_markup=keyboard)
    except Exception as e:
        bot.send_message(message.chat.id, text='Сервер не ответил, попробуйте позже')

# CALLBACKQUERY FROM KEYBOARD
@bot.callback_query_handler(lambda call: call.data.startswith('shop_'))
def handle_shop_query(call):
    shop_id = int(call.data.split('_')[1])
    #Запрос к PostgreSQL для получения данных о выбранном салоне
    cursor.execute("SELECT name, info, image_url FROM shops WHERE id = %s", (shop_id,))
    shop_data = cursor.fetchone()

    if shop_data:
        shop_name, info_text, image_url = shop_data
        message_text = f'Уточняю. Вы выбрали салон: {shop_name}\n Информация о салоне: {info_text}'
        bot.send_mesage(call.message.chat.id, message_text, parse_mode='HTML', reply_markup=review())
        if image_url:
            bot.send_photo(call.message.chat.id, photo=image_url)
    else:
        bot.send_message(call.message.chat.id, text='Салон не найден в базе данных')

# ПРОВЕРКА ОТПРАВЛЕННОГО ПОЛЬЗОВАТЕЛЕМ СООБЩЕНИЯ 
@bot.message_handler(func=lambda message: True)
def handle_text_message(message):
    try:
        user_message = message.text.strip()

        cursor.execute("SELECT id, name FROM shops WHERE name ILIKE %s", (user_message,))
        shop_data = cursor.fetchone()

        if shop_data:
            shop_name, info_text, image_url = shop_data
            message_text = f'Уточняю. Вы выбрали салон: {shop_name}\n Информация о салоне: {info_text}'
            bot.send_mesage(message.chat.id, message_text, parse_mode='HTML', reply_markup=review())
            if image_url:
                bot.send_photo(message.chat.id, photo=image_url)
        else:
            bot.send_message(message.chat.id, text='Салон не найден в базе данных')
    except Exception as e:
        bot.send_message(message.chat.id, "Не понял вашего соообщения, либо учебик не найден")

# REVIEW 
def review():
    keyboard = types.ReplyKeyboardMarkup(row_width=2)
    yes_button = types.KeyboardButton(text='Да', callback_data=f'review_yes')
    no_button = types.KeyboardButton(text='Нет', callback_data=f'review_no')
    keyboard.add(yes_button, no_button)


# REVIEW CALLBACK
@bot.callback_query_handler(lambda call: call.data.startwith('review_'))
def handle_review_query(call):
    pass    

# ПРОВЕРКА ОТПРАВЛЕННЕГО С WEB APP СООБЩЕНИЯ
@bot.message_handler(content_types="web_app_data") #получаем отправленные данные 
def answer(webAppMes):
   print(webAppMes.web_app_data.data) #конкретно то что мы передали в бота
   bot.send_message(webAppMes.chat.id, f"Спасибо, запрос о записи отправлен менеджеру. Вы выбрали: {webAppMes.web_app_data.data}") 
   #отправляем сообщение в ответ на отправку данных из веб-приложения 

if __name__ == '__main__':
    bot.infinity_polling()


# import telebot
# from telebot import types

# TOKEN = '6534971012:AAEXWo4l06RS8U-6nzXbrwmGVy5YnUZNBIs'

# bot = telebot.TeleBot(TOKEN)

# def webAppKeyboard():
#     keyboard = types.ReplyKeyboardMarkup(row_width=1)
#     webAppTest = types.WebAppInfo('https://web-app-telegram-site.vercel.app/')
#     one_button = types.KeyboardButton(text='Конструктор и запись', web_app=webAppTest)
#     keyboard.add(one_button)

#     return keyboard

# #/start
# @bot.message_handler(commands=['start'])
# def send_welcome(message):
#             # Отправляем гифку
#         sticker_id = 'CAACAgIAAxkBAAEKxHNlVmqDS5OS1wg6tPWy-luHOluKjgAC3AUAAj-VzArxX-zMZBcVlzME'  # Замените на реальную ссылку на ваш стикер
#         bot.send_sticker(message.chat.id, sticker_id)

#         # Отправляем приветственное сообщение
#         welcome_message = (
#         "Добро пожаловать в IMEL!\n"
#         "IMEL – система, разрабатываемая для студий маникюра и салонов красоты, позволяющая оптимизировать процесс создания дизайна ногтей,"
#         "подготовки мастера к работе с отдельным клиентом, предоставляющая аналитику на основе выбранных дизайнов"
#         "Создайте заранее запись, используя конструктор (кнопка в меню)\n"
#         "Выберите учебник:"
#         )

#         bot.send_message(message.chat.id, welcome_message, reply_markup=webAppKeyboard())

# @bot.message_handler(content_types="web_app_data") #получаем отправленные данные 
# def answer(webAppMes):
#    print(webAppMes.web_app_data.data) #конкретно то что мы передали в бота
#    bot.send_message(webAppMes.chat.id, f"Спасибо, запрос о записи отправлен менеджеру. Вы выбрали: {webAppMes.web_app_data.data}") 
#    #отправляем сообщение в ответ на отправку данных из веб-приложения 

# if __name__ == '__main__':
#     bot.infinity_polling()