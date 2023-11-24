import telebot
from telebot import types
import os
import psycopg2 

TOKEN = '6534971012:AAEXWo4l06RS8U-6nzXbrwmGVy5YnUZNBIs'

bot = telebot.TeleBot(TOKEN)

DATABASE_URL = 'postgresql://postgres:*AeGBca5aCbaB2FCgG1D*ceG2cE53BBF@viaduct.proxy.rlwy.net:10051/railway'


# CONNECTING TO DATABASE
try:
    conn = psycopg2.connect(DATABASE_URL, sslmode='require')
    cursor = conn.cursor()
    print("Connected to PostgresSQL Database")
except psycopg2.OperationalError as e:
    print(f"Failed to connet to PostgreSQL:  {e}")


# Создаем таблицу users, если её нет
cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id SERIAL PRIMARY KEY,
        telegram_id INTEGER UNIQUE,
        selected_shop_id INTEGER
    )
""")
conn.commit()

def webAppKeyboard():
    keyboard = types.ReplyKeyboardMarkup(row_width=1)
    webAppTest = types.WebAppInfo('https://web-app-telegram-site.vercel.app/')
    one_button = types.KeyboardButton(text='Конструктор и запись', web_app=webAppTest)
    keyboard.add(one_button)

    return keyboard

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
            "Создайте заранее запись используя конструктор (кнопка в меню)\n"
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

# Обработка callback от выбора магазина
@bot.callback_query_handler(lambda call: call.data.startswith('shop_'))
def handle_shop_query(call):
    shop_id = int(call.data.split('_')[1])
    user_id = call.from_user.id

    # Отправляем сообщение о выбранном салоне
    cursor.execute("SELECT name, info, image_url FROM shops WHERE id = %s", (shop_id,))
    shop_data = cursor.fetchone()

    if shop_data:
        shop_name, info_text, image_url = shop_data
        message_text = f'Вы выбрали салон: {shop_name}\n Информация о салоне: {info_text}'
        bot.send_message(call.message.chat.id, message_text, parse_mode='HTML')
        if image_url:
            bot.send_photo(call.message.chat.id, photo=image_url)

        # Спрашиваем пользователя, хочет ли он выбрать этот салон
        choose_shop_keyboard = types.InlineKeyboardMarkup(row_width=2)
        yes_button = types.InlineKeyboardButton(text='Выбрать салон', callback_data=f'choose_shop_yes_{shop_id}')
        no_button = types.InlineKeyboardButton(text='Нет', callback_data=f'choose_shop_no_{shop_id}')
        choose_shop_keyboard.add(yes_button, no_button)
        bot.send_message(call.message.chat.id, "Хотите выбрать этот салон?", reply_markup=choose_shop_keyboard)

    else:
        bot.send_message(call.message.chat.id, text='Салон не найден в базе данных')

# Обработка текстовых сообщений от пользователя
@bot.message_handler(func=lambda message: True)
def handle_text_message(message):
    try:
        user_message = message.text.strip()

        # Пытаемся найти салон по введенному пользователем названию
        cursor.execute("SELECT id, name, info, image_url FROM shops WHERE name ILIKE %s", (user_message,))
        shop_data = cursor.fetchone()

        if shop_data:
            shop_id, shop_name, info_text, image_url = shop_data
            message_text = f'Вы выбрали салон: {shop_name}\n Информация о салоне: {info_text}'
            bot.send_message(message.chat.id, message_text, parse_mode='HTML')
            if image_url:
                bot.send_photo(message.chat.id, photo=image_url)

            # Спрашиваем пользователя, хочет ли он выбрать этот салон
            choose_shop_keyboard = types.InlineKeyboardMarkup(row_width=2)
            yes_button = types.InlineKeyboardButton(text='Выбрать салон', callback_data=f'choose_shop_yes_{shop_id}')
            no_button = types.InlineKeyboardButton(text='Нет', callback_data=f'choose_shop_no_{shop_id}')
            choose_shop_keyboard.add(yes_button, no_button)
            bot.send_message(message.chat.id, "Хотите выбрать этот салон?", reply_markup=choose_shop_keyboard)

        else:
            bot.send_message(message.chat.id, text='Салон не найден в базе данных')

    except Exception as e:
        print(e)
        bot.send_message(message.chat.id, "Произошла ошибка при обработке вашего сообщения")


# # Callback для выбора салона
# @bot.callback_query_handler(lambda call: call.data.startswith('choose_shop_yes_') or call.data.startswith('choose_shop_no_'))
# def handle_choose_shop_query(call):
#     user_id = call.from_user.id
#     action, shop_id = call.data.split('_')[2], call.data.split('_')[3]

#     if action == 'yes':
#         # Обработка случая, когда пользователь хочет выбрать салон
#         cursor.execute("UPDATE users SET selected_shop_id = %s WHERE telegram_id = %s", (shop_id, user_id))
#         conn.commit()
#         bot.send_message(call.message.chat.id, "Салон успешно выбран! Используйте конструктор, чтобы изменить или создать новую запись!", reply_markup=webAppKeyboard())

#     elif action == 'no':
#         bot.send_message(call.message.chat.id, "Ок, вы можете выбрать салон позже.")

# Callback для выбора салона
@bot.callback_query_handler(lambda call: call.data.startswith('choose_shop_yes_') or call.data.startswith('choose_shop_no_'))
def handle_choose_shop_query(call):
    user_id = call.from_user.id
    action, shop_id = call.data.split('_')[2], call.data.split('_')[3]

    if action == 'yes':
        # Обработка случая, когда пользователь хочет выбрать салон
        cursor.execute("UPDATE users SET selected_shop_id = %s WHERE telegram_id = %s", (shop_id, user_id))
        conn.commit()

        # Проверяем наличие номера телефона в базе данных
        cursor.execute("SELECT phone_number FROM users WHERE telegram_id = %s", (user_id,))
        existing_phone_number = cursor.fetchone()

        if existing_phone_number:
            # Если номер телефона уже существует, предлагаем пользователю обновить его или пропустить
            update_phone_keyboard = types.InlineKeyboardMarkup(row_width=2)
            update_button = types.InlineKeyboardButton(text='Обновить номер', callback_data='update_phone')
            skip_button = types.InlineKeyboardButton(text='Пропустить', callback_data='skip_phone_update')
            update_phone_keyboard.add(update_button, skip_button)

            bot.send_message(call.message.chat.id, f"Ваш текущий номер телефона: {existing_phone_number[0]}", reply_markup=update_phone_keyboard)
        else:
            # Если номера телефона нет, просим пользователя ввести его
            bot.send_message(call.message.chat.id, "Пожалуйста, введите свой номер телефона:")

            # Регистрируем следующее сообщение пользователя для обработки
            bot.register_next_step_handler(call.message, handle_phone_input)

    elif action == 'no':
        bot.send_message(call.message.chat.id, "Ок, вы можете выбрать салон позже.")

# Функция для обработки введенного номера телефона
def handle_phone_input(message):
    user_id = message.from_user.id
    phone_number = message.text

    # Здесь вы можете добавить дополнительную валидацию номера телефона

    # Обновляем номер телефона в базе данных пользователя
    cursor.execute("UPDATE users SET phone_number = %s WHERE telegram_id = %s", (phone_number, user_id))
    conn.commit()

    bot.send_message(message.chat.id, f"Спасибо! Номер телефона {phone_number} успешно сохранен. Используйте конструктор, чтобы изменить или создать новую запись!", reply_markup=webAppKeyboard())

# Callback для выбора обновления номера телефона
@bot.callback_query_handler(lambda call: call.data == 'update_phone')
def handle_update_phone_query(call):
    bot.send_message(call.message.chat.id, "Пожалуйста, введите новый номер телефона:")

    # Регистрируем следующее сообщение пользователя для обработки
    bot.register_next_step_handler(call.message, handle_phone_input)

# Callback для выбора пропуска обновления номера телефона
@bot.callback_query_handler(lambda call: call.data == 'skip_phone_update')
def handle_skip_phone_update_query(call):
    bot.send_message(call.message.chat.id, "Вы решили пропустить обновление номера. Используйте конструктор, чтобы изменить или создать новую запись!", reply_markup=webAppKeyboard())


# ПРОВЕРКА ОТПРАВЛЕННЕГО С WEB APP СООБЩЕНИЯ
@bot.message_handler(content_types="web_app_data")
def answer(webAppMes):
    user_id = webAppMes.from_user.id
    selected_data = webAppMes.web_app_data.data
    print(webAppMes.web_app_data.data) #конкретно то что мы передали в бота

    # Проверяем, существует ли пользователь в базе данных
    cursor.execute("SELECT id FROM users WHERE telegram_id = %s", (user_id,))
    existing_user = cursor.fetchone()

    if existing_user:
        # Если пользователь существует, обновляем данные
        cursor.execute("UPDATE users SET selected_data = %s WHERE telegram_id = %s", (selected_data, user_id))
    else:
        # Если пользователя нет, добавляем его в базу данных
        cursor.execute("INSERT INTO users (telegram_id, selected_data) VALUES (%s, %s)", (user_id, selected_data))

    conn.commit()

    bot.send_message(webAppMes.chat.id, f"Спасибо, данные успешно сохранены в базе данных. Вы выбрали: {selected_data}")



if __name__ == '__main__':
    bot.infinity_polling()


# # CALLBACKQUERY FROM KEYBOARD
# @bot.callback_query_handler(lambda call: call.data.startswith('shop_'))
# def handle_shop_query(call):
#     shop_id = int(call.data.split('_')[1])
#     user_id = call.from_user.id

#     # Проверяем, есть ли пользователь в базе
#     cursor.execute("SELECT id FROM users WHERE telegram_id = %s", (user_id,))
#     existing_user = cursor.fetchone()
#     if existing_user:
#             # Если пользователь уже существует, обновляем выбранный магазин
#             cursor.execute("UPDATE users SET selected_shop_id = %s WHERE telegram_id = %s", (shop_id, user_id))
#     else:
#         # Если пользователь не существует, добавляем его в базу
#         cursor.execute("INSERT INTO users (telegram_id, selected_shop_id) VALUES (%s, %s)", (user_id, shop_id))

#     conn.commit()

#     #Запрос к PostgreSQL для получения данных о выбранном салоне
#     cursor.execute("SELECT name, info, image_url FROM shops WHERE id = %s", (shop_id,))
#     shop_data = cursor.fetchone()

#     if shop_data:
#         shop_name, info_text, image_url = shop_data
#         message_text = f'Уточняю. Вы выбрали салон: {shop_name}\n Информация о салоне: {info_text}'
#         bot.send_message(call.message.chat.id, message_text, parse_mode='HTML')
#         if image_url:
#             bot.send_photo(call.message.chat.id, photo=image_url)
#     else:
#         bot.send_message(call.message.chat.id, text='Салон не найден в базе данных')


# @bot.message_handler(func=lambda message: True)
# def handle_text_message(message):
#     try:
#         user_message = message.text.strip()

#         cursor.execute("SELECT id, name, info, image_url FROM shops WHERE name ILIKE %s", (user_message,))
#         shop_data = cursor.fetchone()

#         if shop_data:
#             shop_id, shop_name, info_text, image_url = shop_data
#             message_text = f'Уточняю. Вы выбрали салон: {shop_name}\nИнформация о салоне: {info_text}'
#             bot.send_message(message.chat.id, message_text, parse_mode='HTML')

#             if image_url:
#                 bot.send_photo(message.chat.id, photo=image_url)
#         else:
#             bot.send_message(message.chat.id, text='Салон не найден в базе данных')

#     except Exception as e:
#         print(e)
#         bot.send_message(message.chat.id, "Произошла ошибка при обработке вашего сообщения")


# # REVIEW 
# def review():
#     keyboard = types.ReplyKeyboardMarkup(row_width=2)
#     yes_button = types.KeyboardButton(text='Да', callback_data=f'review_yes')
#     no_button = types.KeyboardButton(text='Нет', callback_data=f'review_no')
#     keyboard.add(yes_button, no_button)


# # REVIEW CALLBACK
# @bot.callback_query_handler(lambda call: call.data.startwith('review_'))
# def handle_review_query(call):
#     pass    


# OLD OLD OLD OLD OLD OLD
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
