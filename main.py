import configparser
import os
import asyncio
import sqlite3

from aiogram import Bot, Dispatcher, types, F
from aiogram.filters.command import Command
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
import pandas as pd

from services import fetch_prices, formatting_to_print
from dao import ProductDAO


# Settings
class UploadExcel(StatesGroup):
    waiting_for_file = State()

SETTING_FILE = 'settings.ini'

config = configparser.ConfigParser()
try:
    config.read(SETTING_FILE, encoding='utf-8')

    BOT_TOKEN = config['MAIN']['BOT_TOKEN']
    FILES_FOLDER = config['MAIN']['FILES_FOLDER']
    DB_NAME = config['MAIN']['DB_NAME']
except KeyError:
    print(f'Decoding error: the file "{SETTING_FILE}" is corrupted!')
    os._exit(0)

if not os.path.exists(FILES_FOLDER):
    os.makedirs(FILES_FOLDER)

# Bot initialization
bot = Bot(token=BOT_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(storage=storage)
upload_button = KeyboardButton(text='Upload Excel')
keyboard = ReplyKeyboardMarkup(keyboard=[[upload_button]], resize_keyboard=True, one_time_keyboard=True)

# Start
@dp.message(Command('start'))
async def cmd_start(message: types.Message, state: FSMContext):
    await state.clear()
    await message.answer('Press the button below to upload an Excel file.', reply_markup=keyboard)

# Button click handling
@dp.message(F.text == 'Upload Excel')
async def ask_file(message: types.Message, state: FSMContext):
    await message.answer('Please send the Excel file (.xlsx or .xls).')
    await state.set_state(UploadExcel.waiting_for_file)

# File upload handler
@dp.message(UploadExcel.waiting_for_file, F.content_type == 'document')
async def handle_document(message: types.Message, state: FSMContext):
    file_name = message.document.file_name.lower()
    if file_name.endswith('.xlsx') or file_name.endswith('.xls'):
        # save excel file
        file = await bot.get_file(message.document.file_id)
        downloaded_file = await bot.download_file(file.file_path)
        file_path = f'{FILES_FOLDER}/{file_name}'
        with open(file_path, 'wb') as f:
            f.write(downloaded_file.getbuffer())

        # work with excel file
        try:
            df = pd.read_excel(file_path)
            preview = formatting_to_print(df).to_string()
            await message.answer(f'The file has been successfully received and saved!\n\nPreview:\n{preview}')
        except Exception as ex:
            await message.answer(f'The file was saved, but there is an error: {ex}')
        else:
            df = df.dropna()

            await message.answer('Loading prices...')
            df['price'] = fetch_prices(df)

            # if was a problem with scraping so it is None/NaN
            exception_prices = df[df['price'].isna()]
            if not exception_prices.empty:
                await message.answer(f'There were some problems scraping the price.\n\n'
                                     f'Preview:\n{exception_prices[["url"]].head().to_string()}')

            # show results
            df = df.dropna()
            message_text = f'Prices successfully added!\n\nPreview:<pre>{df[["title", "price"]].head().to_string()}</pre>'
            await message.answer(message_text, parse_mode='HTML')

            # save to db
            dao = ProductDAO(DB_NAME)
            products = df.to_dict(orient='records')
            try:
                dao.bulk_insert_or_update(products)
            except sqlite3.OperationalError as ex:
                print(f'Database access error: {e}')
            finally:
                dao.close()

            # count average prices by product
            grouped = df.groupby('title')['price'].mean()
            message_text = f'Average prices by product.\n\nPreview:<pre>{grouped.head().to_string()}</pre>'
            await message.answer(message_text, parse_mode='HTML')

            await state.clear()
    else:
        await message.answer('Please send the Excel file (.xlsx or .xls).')

# Handler for other messages
@dp.message()
async def other_messages(message: types.Message, state: FSMContext):
    current_state = await state.get_state()
    if current_state is not None:
        await message.answer('Please send the Excel file (.xlsx or .xls).')
    else:
        await message.answer('Click the "Upload Excel" button to get started.')


if __name__ == "__main__":
    asyncio.run(dp.start_polling(bot))