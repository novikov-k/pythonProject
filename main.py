import gspread
import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from oauth2client.service_account import ServiceAccountCredentials
import re
import psycopg2
from config import host, user, password, db_name

bot_token = '6710319437:AAG-zh8y6oc0gAKRxn4yWTm-rIwDSn0A0UM'
chat_id = '-4056194745'
scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
credentials = ServiceAccountCredentials.from_json_keyfile_name('molten-acumen-402718-160511404f88.json', scope)
client = gspread.authorize(credentials)
sheet = client.open('ФИЛИАЛЫ №2').worksheet('ТЕСТ')
bot = Bot(token=bot_token)
dp = Dispatcher(bot, storage=MemoryStorage())
counter = 1
orders = []
orders_row = []
last_row = len(sheet.col_values(6))

connection = psycopg2.connect(host=host, user=user, password=password, database=db_name)
cursor = connection.cursor()


def run_in_executor(func):
    def wrapper(*args, ):
        loop = asyncio.get_event_loop()
        new_args = [arg for arg in args]
        return loop.run_in_executor(None, func, *new_args)

    return wrapper


def value(row):
    global last_row
    global counter
    new_value1 = sheet.cell(last_row + counter, row).value
    return new_value1


def new_value(row):
    global last_row
    global counter
    new_value2 = sheet.cell(last_row + counter - 1, row).value
    return new_value2


def buttons():
    markup = types.InlineKeyboardMarkup()
    accept_button = types.InlineKeyboardButton(text='Принять', callback_data='accept')
    reject_button = types.InlineKeyboardButton(text='Отклонить', callback_data='reject')
    markup.row(accept_button, reject_button)
    return markup


def buttons1(order_index):
    markup = types.InlineKeyboardMarkup()
    preparing_button = types.InlineKeyboardButton(text='Статус: готовится',
                                                  callback_data='preparing' + str(order_index))
    delivering_button = types.InlineKeyboardButton(text='Статус: едет к клиенту',
                                                   callback_data='delivering' + str(order_index))
    completed_button = types.InlineKeyboardButton(text='Статус: завершен', callback_data='completed' + str(order_index))
    markup.row(preparing_button, delivering_button, completed_button)
    return markup


async def check_all():
    global last_row
    global counter
    global chat_id
    global orders
    global orders_row
    global cursor
    if sheet.cell(last_row + counter, 6).value != sheet.cell(last_row + counter + 1, 6).value:
        composition = ""
        count_comp = 0
        composition += str(value(20)) + " "
        while sheet.cell(last_row + counter, 21 + count_comp).value != sheet.cell(last_row + counter,
                                                                                  21 + count_comp + 2).value:
            composition += str(value(21 + count_comp)) + ' '
            count_comp += 2
        message = ('Адрес: ' + str(value(6)) + '\nНомер: ' + str(
            value(7)) + '\nВремя заказа: ' + str(value(9)) + '\nСостав заказа: ' + composition +
                   '\nПалочки: ' + str(value(14)) + '\nCоевый соус: ' + str(
                    value(15)) + '\nИмбирь: ' + str(value(16)) + '\nВасаби: ' + str(
                    value(17)) + '\nСпособ оплаты: ' + str(value(18)) + '\nИтоговая цена: ' + str(
                    value(19)))
        orders_row.append(last_row + counter)
        orders.append(message)
        await bot.send_message(chat_id, "Новый заказ! \n" + message, reply_markup=buttons())
        counter += 1
        print("Алло уёба заказ пришел")


async def inf_loop():
    while True:
        await check_all()
        await asyncio.sleep(15)


async def printer():
    global last_row
    global counter
    global chat_id
    global orders
    global orders_row
    composition = ""
    food_comp = ""
    count_comp = 0
    composition += str(new_value((20+count_comp))) + " "
    food_name = str(new_value(20 + count_comp))
    try:
        query = f"SELECT food_comp FROM list WHERE food = '{food_name}'"
        cursor.execute(query)
        result = cursor.fetchone()
        food_comp += result[0] + "\n \n"
    except Exception as ex:
        food_comp += "Ошибка в парсинге" + "\n"
    while sheet.cell(last_row + counter - 1, 21 + count_comp).value != sheet.cell(last_row + counter - 1,
                                                                                  21 + count_comp + 2).value:
        composition += str(new_value(21 + count_comp)) + ' '
        food_name = str(new_value(21 + count_comp))
        try:
            query = f"SELECT food_comp FROM list WHERE food = '{food_name}'"
            cursor.execute(query)
            result = cursor.fetchone()
            food_comp += result[0] + "\n \n"
        except Exception as ex:
            food_comp += "Ошибка в парсинге" + "\n"
        count_comp += 2
    message = ('Адрес: ' + str(new_value(6)) + '\nНомер: ' + str(
        new_value(7)) + '\nВремя заказа: ' + str(new_value(9)) + '\nСостав заказа: ' + composition +
               '\nПалочки: ' + str(new_value(14)) + '\nCоевый соус: ' + str(
                new_value(15)) + '\nИмбирь: ' + str(new_value(16)) + '\nВасаби: ' + str(
                new_value(17)) + '\nСпособ оплаты: ' + str(new_value(18)) + '\nИтоговая цена: ' + str(
                new_value(19)) + "\n")
    message += food_comp
    await bot.send_message(chat_id, message)


@dp.callback_query_handler(lambda call: True)
async def handle_button_click(callback_query: types.CallbackQuery):
    global orders
    global orders_row
    if callback_query.data == 'accept':
        print('Нажали кнопку')
        await printer()
        sheet.update_cell(last_row + counter - 1, 5, 'п')
        message_to_delete = callback_query.message
        await bot.delete_message(chat_id=message_to_delete.chat.id, message_id=message_to_delete.message_id)
        await bot.send_message(chat_id, 'Заказ успешно принят!')
    elif callback_query.data == 'reject':
        message_to_delete = callback_query.message
        await bot.delete_message(chat_id=message_to_delete.chat.id, message_id=message_to_delete.message_id)
        await bot.send_message(chat_id, 'Заказ отклонен.')
    elif re.match(r'^preparing\d+$', callback_query.data):
        order_id = callback_query.data.split("preparing")[1]
        sheet.update_cell(orders_row[int(order_id)], 10, 'готов')
        await bot.send_message(callback_query.message.chat.id, 'Статус заказа ' + order_id + ': Готовится')
    elif re.match(r'^delivering\d+$', callback_query.data):
        order_id = callback_query.data.split("delivering")[1]
        sheet.update_cell(orders_row[int(order_id)], 10, 'в пути')
        await bot.send_message(callback_query.message.chat.id, 'Статус заказа ' + order_id + ': Едет к клиенту')
    elif re.match(r'^completed\d+$', callback_query.data):
        order_id = callback_query.data.split("completed")[1]
        sheet.update_cell(orders_row[int(order_id)], 10, 'выполнен')
        await bot.send_message(callback_query.message.chat.id, 'Статус заказа ' + order_id + ': Завершен')
        print(order_id)
        if order_id:
            orders.pop(int(order_id))
            orders_row.pop(int(order_id))
        message_to_delete = callback_query.message
        await bot.delete_message(chat_id=message_to_delete.chat.id, message_id=message_to_delete.message_id)
    else:
        order_index = int(callback_query.data)
        order = orders[order_index]
        await bot.send_message(callback_query.message.chat.id, order, reply_markup=buttons1(order_index))
        message_to_delete = callback_query.message
        await bot.delete_message(chat_id=message_to_delete.chat.id, message_id=message_to_delete.message_id)


@dp.message_handler(commands=['orders'])
async def orders_handler(message: types.Message):
    global orders

    # Create inline keyboard
    keyboard = types.InlineKeyboardMarkup()

    if orders:
        for i in range(len(orders)):
            order_button = types.InlineKeyboardButton("ID: " + str(i) + "\n" + str(orders[i]), callback_data=str(i))
            keyboard.add(order_button)
        await bot.send_message(message.chat.id, "Все заказы:", reply_markup=keyboard)
    else:
        await bot.send_message(message.chat.id, "В данный момент заказов нет.")


async def main():
    polling_task = asyncio.create_task(dp.start_polling())
    loop_task = asyncio.create_task(inf_loop())
    await asyncio.gather(polling_task, loop_task)


if __name__ == '__main__':
    asyncio.run(main())
