from aiogram import Bot, Dispatcher, executor, types
from aiogram.types import ReplyKeyboardMarkup, ReplyKeyboardRemove, KeyboardButton
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Command
from aiogram.dispatcher.filters.state import State, StatesGroup
import MySQLdb
from datetime import datetime
import logging
from main import chat_anwser
from menu import responsemenu
import json
import requests

# logging.basicConfig(level=logging.INFO)

TOKEN = "5578817522:AAEx2Ag3nE3hvsHDCPBuzTxt0JZ03U-4qak"

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
urlmenu = "http://localhost:3000/restoran/image"
body = {"idRestoran":29}

responsemenu = requests.post(urlmenu, json=body)

if responsemenu.status_code == 200:
    dataMenu = json.loads(responsemenu.text)
    link = dataMenu['data']
    print(link)
    gambar = open(f"c:\Skripsi\skripsi-api\image\{link}", 'rb')
    print(gambar)
else:
    print(f"Error: {responsemenu.status_code}")
    print(f"Error: {responsemenu.text}")
# data = json.loads(responsemenu.text)
# link = data['data']
# gambar = open(f"C:\Skripsi\skripsi-api-master\image\{link}", 'rb')

urlmeja = "http://localhost:3000/restoran/jumlahMeja"
body = {"idRestoran": 29}
responsemeja = requests.post(urlmeja, json=body)
dataMeja = json.loads(responsemeja.text)
value = dataMeja['data'][0]['jumlahMeja']
for i in range(1, value+1):
    button_code = f"buttonmeja{i} = KeyboardButton('{i}')"
    exec(button_code)

## Tombol input nomor meja
#buttonmeja1 = KeyboardButton("1")
#buttonmeja2 = KeyboardButton("2")
#buttonmeja3 = KeyboardButton("3")
#buttonmeja4 = KeyboardButton("4")
#buttonmeja5 = KeyboardButton("5")
#buttonmeja6 = KeyboardButton("6")

## Tombol input menu pesanan
urlmenu = "http://localhost:3000/menu/getAllMenuIdRestoran"
body = {"idRestoran": 29}
responsemenu = requests.post(urlmenu, json=body)
data = json.loads(responsemenu.text)
menu_items = [item['nama'] for item in data['data']]

keyboardmenu = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
buttonsudah = KeyboardButton("sudah")

for item in menu_items:
    print(item)
    button = KeyboardButton(f"{item}")
    print(button)
    keyboardmenu.add(button)
    if item == menu_items[-1]:
        keyboardmenu.add(buttonsudah)

    
#buttonmenu1 = KeyboardButton("nasi goreng")
#buttonmenu2 = KeyboardButton("mie goreng")
#buttonmenu3 = KeyboardButton("mie rebus")


## Tombol input jumlah menu pesanan
buttonjmlmenu1 = KeyboardButton("1")
buttonjmlmenu2 = KeyboardButton("2")
buttonjmlmenu3 = KeyboardButton("3")

## Fungsi tombol input nomor meja
keyboardnomeja = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True).add(
    *[globals()[f"buttonmeja{i}"] for i in range(1,11)]
    )

## Fungsi tombol input menu
#keyboardmenu = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True).add(
#    buttonmenu1,
#    buttonmenu2,
#    buttonmenu3,
#    buttonsudah
#    )

## Fungsi tombol jumlah pesanan
keyboardjmlmenu = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True).add(
    buttonjmlmenu1,
    buttonjmlmenu2,
    buttonjmlmenu3
    )


### Awalan
@dp.message_handler(Command("start"))
async def start(message: types.Message):
    start_answer = "Halo! Selamat datang, disini kamu bisa tanya-tanya dulu loh cara pesannya gimana"
    print(start_answer)
    await message.answer(start_answer)

### Menampilkan Menu lewat commands
@dp.message_handler(commands="menu")
async def menu(message: types.Message):
    image = gambar
    with open(f"C:\Skripsi\skripsi-api\image\{link}", 'rb') as photo:
        await bot.send_photo(message.chat.id, photo)
        await message.answer("Ini menunya ya kak")

### Awalan untuk mulai memesan makanan
@dp.message_handler(Command("mulai"))
async def start(message: types.Message):
    mulai_answer = "Halo kamu sekarang ada di mode untuk memesan ya. Kamu di meja berapa kak?"
    print(mulai_answer)
    await MyStates.FIRST_STATE.set()
    await message.answer(mulai_answer, reply_markup=keyboardnomeja)

varTransaksi = None
## Data jumlah meja
dataJumlahMeja = 10
jumlahMeja = {}

for meja in range(dataJumlahMeja):
    meja += 1
    jumlahMeja[f"{meja}"] = f"Oke, kamu di meja nomor {meja} ya, tekan tombol di bawah ini untuk menampilkan menunya dan lanjut ke langkah selanjutnya"

meja_response = jumlahMeja

# print(jumlahMeja[int(nomor)])

### Fungsi tombol input nomor meja
@dp.message_handler(state=MyStates.FIRST_STATE)
async def kb_nomeja(message: types.Message, state: FSMContext):
    #meja_answer = "Oke, kamu di meja nomor berapa kak?"
    #await message.answer(meja_answer, reply_markup=keyboardnomeja)

    urlmeja = "http://localhost:3000/transaksi/postTransaksi"
    username = message["from"]["username"]
    nomorMeja = message["text"]
    print(nomorMeja)
    body = {
        "username": username,
        "nomorMeja": int(nomorMeja),
        "idRestoran":29
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
    
    response_meja = meja_response.get(message.text)

    if response_meja is not None:
        await MyStates.SECOND_STATE.set()
        await message.reply(response_meja)

### Menampilkan Menu lewat state
@dp.message_handler(state=MyStates.SECOND_STATE)
async def menu(message: types.Message, state: FSMContext):
    image = gambar
    with open(f"C:\Skripsi\skripsi-api\image\{link}", 'rb') as photo:
        await bot.send_photo(message.chat.id, photo)
    await MyStates.THIRD_STATE.set()
    await message.answer("Ini menunya ya kak, mau pesan apa?", reply_markup=keyboardmenu)

varidmenu = None

### Fungsi tombol input menu pesanan
@dp.message_handler(state=MyStates.THIRD_STATE)
async def kb_pesanmenu(message: types.Message, state: FSMContext):
    global varTransaksi
    await message.answer("Okeeee")
    idTransaksi = varTransaksi
    print("Ini idTransaksi: ", idTransaksi)

    urlmenu = "http://localhost:3000/menu/getAllMenuIdRestoran"
    body = {"idRestoran":29}
    responsemenu = requests.post(urlmenu, json=body)
    data = json.loads(responsemenu.text)
    menu_items = [item['nama'] for item in data['data']]

    global varidmenu
    namaMenu = menu_items[0]  # Mengambil menu pertama sebagai default
    if message.text in menu_items:
        namaMenu = message.text

        res = data["data"]
        for r in res:
            if r["nama"] == message.text:
                varidmenu = r["idMenu"]
                print("Ini idMenu: ", varidmenu)
                break

        await MyStates.FOURTH_STATE.set()
        await message.reply(f"Kamu pesan {namaMenu}, mau berapa porsi?", reply_markup=keyboardjmlmenu)
    else:
        await state.finish()
        await message.reply("Oke kak siap terima kasih ini notanya ya, silahkan ke kasir untuk membayar")
        
### Fungsi input jumlah menu pesanan
@dp.message_handler(state=MyStates.FOURTH_STATE)
async def kb_jmlmenu(message: types.Message, state: FSMContext):
    global varTransaksi
    await message.answer("Okeeee")
    idTransaksi = varTransaksi
    print("Ini idTransaksi: ", idTransaksi)

    if message.text == "1":
        qty = message.text
        await state.set_state(state=MyStates.THIRD_STATE)
        await message.reply("Pesan apa lagi kak?, kalo udah tekan tombol di bawah ini ya kak", reply_markup=keyboardmenu)
    elif message.text == "2":
        qty = message.text
        await state.set_state(state=MyStates.THIRD_STATE)
        await message.reply("Pesan apa lagi kak?, kalo udah tekan tombol di bawah ini ya kak", reply_markup=keyboardmenu)
    elif message.text == "3":
        qty = message.text
        await state.set_state(state=MyStates.THIRD_STATE)
        await message.reply("Pesan apa lagi kak?, kalo udah tekan tombol di bawah ini ya kak", reply_markup=keyboardmenu)
    

    global varidmenu
    urlpesan = "http://localhost:3000/transaksi/postPesanan"
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

### NLP
@dp.message_handler()
async def convo(message: types.Message):
    jawabconvo = chat_anwser(message["text"])
    print(jawabconvo)
    print(message)
    await message.answer(jawabconvo)

if __name__ == '__main__':
    try:
        executor.start_polling(dispatcher=dp, skip_updates=True)
    
    except Exception as error:
        print('Cause: {}'.format(error))