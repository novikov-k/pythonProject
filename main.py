import gspread
import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram import executor
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from oauth2client.service_account import ServiceAccountCredentials

bot_token = '6710319437:AAG-zh8y6oc0gAKRxn4yWTm-rIwDSn0A0UM'
chat_id = '-4056194745'
scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
credentials = ServiceAccountCredentials.from_json_keyfile_name('testprj-402613-5daa36fbb50d.json', scope)
client = gspread.authorize(credentials)
sheet = client.open('Teststesttest').sheet1
bot = Bot(token=bot_token)
dp = Dispatcher(bot, storage=MemoryStorage())
counter = 1
last_row = len(sheet.col_values(6))


def run_in_executor(func):
    def wrapper(*args, **kwargs):
        loop = asyncio.get_event_loop()
        new_args = [arg for arg in args]
        return loop.run_in_executor(None, func, *new_args, **kwargs)

    return wrapper


def value(row):
    global last_row
    global counter
    new_value = sheet.cell(last_row + counter, row).value
    return new_value


def buttons():
    markup = types.InlineKeyboardMarkup()
    accept_button = types.InlineKeyboardButton(text='Принять', callback_data='accept')
    reject_button = types.InlineKeyboardButton(text='Отклонить', callback_data='reject')
    markup.row(accept_button, reject_button)
    return markup


async def check_all():
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
        await bot.send_message(chat_id, message, reply_markup=buttons())
        counter += 1
        print("Алло уеба заказ пришел")


async def inf_loop():
    while True:
        await check_all()
        await asyncio.sleep(15)


@dp.callback_query_handler(lambda call: True)
async def handle_button_click(callback_query: types.CallbackQuery):
    if callback_query.data == 'accept':
        print('Нажали кнопку')
        sheet.update_cell(last_row + counter - 1, 5, 'п')
        await bot.send_message(chat_id, 'Заказ успешно принят!')
    elif callback_query.data == 'reject':
        message_to_delete = callback_query.message
        await bot.delete_message(chat_id=message_to_delete.chat.id, message_id=message_to_delete.message_id)
        await bot.send_message(chat_id, 'Заказ отклонен.')


@dp.message_handler(content_types=types.ContentTypes.TEXT)
async def send_text(message: types.Message):
    print("кто-то что-то написал")
    if message.text == 'Принять':
        sheet.update_cell(last_row + counter, 5, 'п')
        await bot.send_message(chat_id, 'Заказ успешно принят!')
    elif message.text == 'Отклонить':
        await bot.send_message(chat_id, 'Заказ отклонен.')


async def main():
    polling_task = asyncio.create_task(dp.start_polling())
    loop_task = asyncio.create_task(inf_loop())
    await asyncio.gather(polling_task, loop_task)


if __name__ == '__main__':
    asyncio.run(main())
