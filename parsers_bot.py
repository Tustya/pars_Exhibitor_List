from aiogram import Bot, types
from aiogram.dispatcher import Dispatcher
from aiogram.utils import executor
from aiogram.dispatcher.filters import Text
from auth_data import token
from main import full_collect


bot = Bot(token=token)
dp = Dispatcher(bot)


@dp.message_handler(commands=['start'])
async def process_start_command(message: types.Message):
    await message.reply('Это бот для парсинга контактов с сайта https://en.hostistanbulfair.com/2023-exhibitor-list.html')
    start_buttons = ['Парсинг контактов']
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add(*start_buttons)

    await message.answer('Выберите действие', reply_markup=keyboard)


@dp.message_handler(Text(equals='Парсинг контактов'))
async def pars_hostistanbulfair(message: types.Message):
    await message.answer('Пожалуйста подождите 5-7 минут...')
    file = full_collect()
    # file = 'data.xlsx'
    await bot.send_document(chat_id=message.chat.id, document=open(file, 'rb'))


if __name__ == '__main__':
    executor.start_polling(dp)

