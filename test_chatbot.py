from aiogram import Bot, Dispatcher, executor, types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Command
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.contrib.fsm_storage.memory import MemoryStorage

# Inisialisasi bot dan dispatcher
bot = Bot(token='5578817522:AAEx2Ag3nE3hvsHDCPBuzTxt0JZ03U-4qak')
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)

# Definisikan states
class MyStates(StatesGroup):
    FIRST_STATE = State()
    SECOND_STATE = State()

# Definisikan handler perintah "/start"
@dp.message_handler(Command('start'))
async def start(message: types.Message):
    # Set state FIRST_STATE
    await MyStates.FIRST_STATE.set()
    await message.reply('Selamat datang! Silakan kirim pesan pertama.')

# Handler untuk menerima pesan pertama
@dp.message_handler(state=MyStates.FIRST_STATE)
async def process_first_message(message: types.Message, state: FSMContext):
    # Lakukan tindakan sesuai pesan pertama
    await message.reply('Pesan pertama diterima.')
    
    # Set state SECOND_STATE
    await MyStates.SECOND_STATE.set()
    await message.reply('Kirim pesan kedua.')

# Handler untuk menerima pesan kedua
@dp.message_handler(state=MyStates.SECOND_STATE)
async def process_second_message(message: types.Message, state: FSMContext):
    # Lakukan tindakan sesuai pesan kedua
    await message.reply('Pesan kedua diterima.')

    # Reset state ke awal
    await state.finish()
    await message.reply('Terima kasih!')

# Mulai polling
executor.start_polling(dp, skip_updates=True)
