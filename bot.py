from aiogram import Bot, Dispatcher, executor, types
from aiogram.types import ReplyKeyboardMarkup,ReplyKeyboardRemove,KeyboardButton
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Command
from aiogram.dispatcher.filters.state import State, StatesGroup
from datetime import datetime
import logging
from main import chat_answer
from menu import responsemenu
import json
import requests
import traceback
from config import TOKEN, RESTAURANT_ID, API_BASE_URL, info_chatbot

# Konfigurasi logger
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Inisialisasi bot dan dispatcher
bot = Bot(token=TOKEN)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)

# Definisikan states
class MyStates(StatesGroup):
    FIRST_STATE = State()
    SECOND_STATE = State()
    THIRD_STATE = State()
    FOURTH_STATE = State()

# Ambil gambar menu dari API
urlgmenu = f"{API_BASE_URL}/restoran/image"
body = {"idRestoran": RESTAURANT_ID}
responsemenu = requests.post(urlgmenu, json=body)

if responsemenu.status_code == 200:
    dataMenu = json.loads(responsemenu.text)
    link = dataMenu['data']
    print(link)
    gambar = open(f"c:\Skripsi\skripsi-api\image\{link}", 'rb')
    print(gambar)
else:
    print(f"Error: {responsemenu.status_code}")
    print(f"Error: {responsemenu.text}")

## Tombol nomor meja
urlmeja = f"{API_BASE_URL}/restoran/jumlahMeja"
body = {"idRestoran": RESTAURANT_ID}

responsemeja = requests.post(urlmeja, json=body)
dataMeja = json.loads(responsemeja.text)
value = dataMeja['data'][0]['jumlahMeja']

keyboardnomeja = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True).add(
    *[KeyboardButton(str(i)) for i in range(1, value+1)]
)

## Tombol input menu pesanan
urlmenu = f"{API_BASE_URL}/menu/getAllMenuIdRestoran"
body = {"idRestoran": RESTAURANT_ID}

responsemenu = requests.post(urlmenu, json=body)
data = json.loads(responsemenu.text)
menu_items = [item['nama'] for item in data['data']]

buttonsudah = KeyboardButton("sudah")
keyboardmenu = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True).add(
    *[KeyboardButton(item) for item in menu_items],
    buttonsudah
)

# Ambil jumlah maksimal menu pesanan dari variabel
max_menu = 10

# Buat daftar tombol jumlah menu pesanan secara dinamis
keyboardjmlmenu = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
for i in range(1, max_menu+1):
    button = KeyboardButton(str(i))
    keyboardjmlmenu.add(button)

### Awalan akan ke NLP Mode
@dp.message_handler(Command("start"))
async def start(message: types.Message):
    try:
        logger.info(f"User {message.from_user.username} memulai chat")
        start_answer = "Halo! Selamat datang, sekarang kamu sedang berada di Mode Chatting dari chatbot ini. Disini kamu bisa tanya-tanya apapun! asal masih ada hubungannya sama restoran ini ya! Oiya jangan lupa untuk pencet tombol /info terlebih dahulu agar tau cara pake chatbot ini ya! Have fun!"
        print(start_answer)
        await message.answer(start_answer)
    except Exception as e:
        traceback.print_exc()
        error_message = "Terjadi kesalahan saat memulai chat"
        await message.answer(error_message)

### Menampilkan Menu lewat commands di NLP Mode
@dp.message_handler(commands="menu")
async def show_menu(message: types.Message):
    try:
        with open(f"C:\Skripsi\skripsi-api\image\{link}", 'rb') as photo:
            await bot.send_photo(message.chat.id, photo)
        await message.answer("Ini untuk menunya ya kak")
    except Exception as e:
        traceback.print_exc()
        error_message = "Terjadi kesalahan saat menampilkan menu"
        await message.answer(error_message)

### Menampilkan Menu lewat commands di NLP Mode
@dp.message_handler(commands="info")
async def show_info(message: types.Message):
    try:
        await message.answer(info_chatbot)
    except Exception as e:
        traceback.print_exc()
        error_message = "Terjadi kesalahan saat menampilkan info"
        await message.answer(error_message)

### Awalan untuk mulai memesan makanan di Mode Pemesanan
@dp.message_handler(Command("pesan"))
async def start_order(message: types.Message):
    try:
        pesan_answer = "Halo kamu sekarang ada di Mode Pemesanan. Kamu sekarang duduk di meja berapa kak?"
        print(pesan_answer)
        await MyStates.FIRST_STATE.set()
        await message.answer(pesan_answer, reply_markup=keyboardnomeja)
    except Exception as e:
        traceback.print_exc()
        error_message = "Terjadi kesalahan saat memulai pemesanan"
        await message.answer(error_message)

varTransaksi = None

### Fungsi tombol input nomor meja
@dp.message_handler(state=MyStates.FIRST_STATE)
async def input_table_number(message: types.Message, state: FSMContext):
    logger.info(f"User {message.from_user.username} memilih nomor meja {message.text}")
    urlmeja = f"{API_BASE_URL}/transaksi/postTransaksi"
    username = message.from_user.username
    nomorMeja = message.text
    print(nomorMeja)
    body = {
        "username": username,
        "nomorMeja": int(nomorMeja),
        "idRestoran": RESTAURANT_ID
    }
    
    global varTransaksi
    responsemeja = requests.post(urlmeja, json=body)
    if responsemeja.status_code == 200:
        transaksi = json.loads(responsemeja.text)
        varTransaksi = transaksi["data"]["idTransaksi"]
        print("Ini idTransaksi: ", varTransaksi)
        
    else:
        print(f"Error: {responsemeja.status_code}")
        print(f"Error: {responsemeja.text}")
    
    meja_response = f"Oke, kamu di meja nomor {nomorMeja} ya, tekan tombol /menu ini untuk menampilkan menunya dan lanjut ke langkah selanjutnya"
    await MyStates.SECOND_STATE.set()
    await message.reply(meja_response)

### Menampilkan Menu lewat state
@dp.message_handler(state=MyStates.SECOND_STATE)
async def show_menu_state(message: types.Message, state: FSMContext):
    with open(f"C:\Skripsi\skripsi-api\image\{link}", 'rb') as photo:
        await bot.send_photo(message.chat.id, photo)
    await MyStates.THIRD_STATE.set()
    await message.answer("Ini untuk menunya ya kak, mau pesan apa? Silahkan tekan tombol yang tersedia ya kak", reply_markup=keyboardmenu)

varidmenu = None

### Fungsi tombol input menu pesanan
@dp.message_handler(state=MyStates.THIRD_STATE)
async def input_order_menu(message: types.Message, state: FSMContext):
    logger.info(f"User {message.from_user.username} memesan menu {message.text}")
    global varTransaksi
    await message.answer("Oke siap kak!")
    idTransaksi = varTransaksi
    print("Ini idTransaksi: ", idTransaksi)

    if message.text in menu_items:
        namaMenu = message.text

        res = data["data"]
        for r in res:
            if r["nama"] == message.text:
                varidmenu = r["idMenu"]
                print("Ini idMenu: ", varidmenu)
                break

        await MyStates.FOURTH_STATE.set()
        await message.reply(f"Kamu pesan {namaMenu} ya kak, mau berapa porsi nih?", reply_markup=keyboardjmlmenu)
    else:
        await state.finish()
        sudahAnswer = "Oke kak siap terima kasih ini notanya ya, silahkan ke kasir untuk membayar"
        await message.reply(sudahAnswer)
        
### Fungsi input jumlah menu pesanan
@dp.message_handler(state=MyStates.FOURTH_STATE)
async def input_order_quantity(message: types.Message, state: FSMContext):
    global varTransaksi
    await message.answer("Okay siap kak!")
    idTransaksi = varTransaksi
    print("Ini idTransaksi: ", idTransaksi)

    if message.text in ["1", "2", "3"]:
        qty = message.text
        await state.set_state(state=MyStates.THIRD_STATE)
        await message.reply("Apakah ada yang mau dipesan lagi kak? Kalo udah silahkan tekan tombol sudahnya ya kak", reply_markup=keyboardmenu)

        urlpesan = f"{API_BASE_URL}/transaksi/postPesanan"
        idtransaksi = idTransaksi
        idmenu = varidmenu
        quantity = qty

        body = {
            "idTransaksi": idtransaksi,
            "idMenu": int(idmenu),
            "qty": int(quantity)
        }

        responsepesan = requests.post(urlpesan, json=body)
        if responsepesan.status_code == 200:
            data = json.loads(responsepesan.text)
            print(data) 
        else:
            print(f"Error: {responsepesan.status_code}")
            print(f"Error: {responsepesan.text}")
    else:
        await state.finish()
        sudahAnswer = "Oke kak siap terima kasih ini notanya ya, silahkan ke kasir untuk membayar"
        await message.reply(sudahAnswer)

### NLP Mode
@dp.message_handler()
async def chat_response(message: types.Message):
    try:
        jawabConvo = chat_answer(message.text)
        print(jawabConvo)
        print(message)
        await message.answer(jawabConvo)
    except Exception as e:
        traceback.print_exc()
        error_message = "Terjadi kesalahan saat memproses pesan"
        await message.answer(error_message)

if __name__ == '__main__':
    try:
        executor.start_polling(dispatcher=dp, skip_updates=True)
        logger.info("Bot dijalankan")
    except Exception as error:
        traceback.print_exc()
        print('Cause: {}'.format(error))
        logger.exception(f"Pesan kesalahan: {error}")