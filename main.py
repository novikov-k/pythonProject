import gspread
import telebot
from oauth2client.service_account import ServiceAccountCredentials

bot_token = '6710319437:AAG-zh8y6oc0gAKRxn4yWTm-rIwDSn0A0UM'
chat_id = '-4056194745'
scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
credentials = ServiceAccountCredentials.from_json_keyfile_name('testprj-402613-5daa36fbb50d.json', scope)
client = gspread.authorize(credentials)
sheet = client.open('Teststesttest').sheet1
bot = telebot.TeleBot(bot_token)
counter = 1
last_row = len(sheet.col_values(6))
bot.send_message(chat_id, 'Готово, епта')


def value(row):
    global last_row
    global counter
    new_value = sheet.cell(last_row + counter, row).value
    return new_value


def buttons():
    markup = telebot.types.InlineKeyboardMarkup()
    accept_button = telebot.types.InlineKeyboardButton(text='Принять', callback_data='accept')
    reject_button = telebot.types.InlineKeyboardButton(text='Отклонить', callback_data='reject')
    markup.row(accept_button, reject_button)
    return markup


@bot.message_handler(func=lambda message: True)
def handle_message(message):
    if message.content_type == 'callback_query':
        if message.data == 'accept':
            sheet.update_cell(last_row + counter, 5, 'п')
            bot.send_message(chat_id, 'Заказ успешно принят!')
        elif message.data == 'reject':
            bot.send_message(chat_id, 'Заказ отклонен.')


@bot.callback_query_handler(func=lambda call: True)
def handle_button_click(callback):
    if callback.data == 'accept':
        print('Нажали кнопку')
        sheet.update_cell(last_row + counter, 5, 'п')  # обновляем значение в столбце E
        bot.send_message(chat_id, 'Заказ успешно принят!')
    elif callback.data == 'reject':
        bot.send_message(chat_id, 'Заказ отклонен.')


def check_all():
    global last_row
    global counter
    global chat_id
    if sheet.cell(last_row + counter, 6).value != sheet.cell(last_row + counter + 1, 6).value:
        message = 'Новый заказ! \n Адрес: ' + str(value(6)) + '\n Номер: ' + str(
            value(7)) + '\n Время заказа: ' + str(value(8)) + '\n Состав заказа: ' + str(
            value(10)) + '\n Палочки: ' + str(value(12)) + '\n Соевый соус: ' + str(
            value(13)) + '\n Имбирь: ' + str(value(14)) + '\n Васаби: ' + str(
            value(15)) + '\n Способ оплаты: ' + str(value(16)) + '\n Итоговая цена: ' + str(
            value(17))
        bot.send_message(chat_id, message, reply_markup=buttons())
        counter += 1
        print("Алло уеба заказ пришел")


def set_trigger():
    import time
    while True:
        check_all()
        time.sleep(60)


set_trigger()

bot.polling()