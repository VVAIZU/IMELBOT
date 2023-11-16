import telebot
from telebot import types
import config

TOKEN = '6534971012:AAEXWo4l06RS8U-6nzXbrwmGVy5YnUZNBIs'

bot = telebot.TeleBot(config.TOKEN)

def webAppKeyboard():
    keyboard = types.ReplyKeyboardMarkup(row_width=1)
    webAppTest = types.WebAppInfo('https://web-app-telegram-site.vercel.app/')
    one_button = types.KeyboardButton(text='Конструктор и запись', web_app=webAppTest)
    keyboard.add(one_button)

    return keyboard

#/start
@bot.message_handler(commands=['start'])
def send_welcome(message):
            # Отправляем гифку
        sticker_id = 'CAACAgIAAxkBAAEKxHNlVmqDS5OS1wg6tPWy-luHOluKjgAC3AUAAj-VzArxX-zMZBcVlzME'  # Замените на реальную ссылку на ваш стикер
        bot.send_sticker(message.chat.id, sticker_id)

        # Отправляем приветственное сообщение
        welcome_message = (
        "Добро пожаловать в IMEL!\n"
        "IMEL – система, разрабатываемая для студий маникюра и салонов красоты, позволяющая оптимизировать процесс создания дизайна ногтей,"
        "подготовки мастера к работе с отдельным клиентом, предоставляющая аналитику на основе выбранных дизайнов"
        "Создайте заранее запись, используя конструктор (кнопка в меню)\n"
        "Выберите учебник:"
        )

        bot.send_message(message.chat.id, welcome_message, reply_markup=webAppKeyboard())

@bot.message_handler(content_types="web_app_data") #получаем отправленные данные 
def answer(webAppMes):
   print(webAppMes.web_app_data.data) #конкретно то что мы передали в бота
   bot.send_message(webAppMes.chat.id, f"Спасибо, запрос о записи отправлен менеджеру. Вы выбрали: {webAppMes.web_app_data.data}") 
   #отправляем сообщение в ответ на отправку данных из веб-приложения 

if __name__ == '__main__':
    bot.infinity_polling()