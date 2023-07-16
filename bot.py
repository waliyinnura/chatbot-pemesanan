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
    awalPesan = State()
    tampilMenu = State()
    inputPesanan = State()
    orderQty = State()
    editPesanan = State()
    inputEditPesanan = State()
    qtyEditPesanan = State()
    cancelPesanan = State()
    deleteMenu = State()
    verifDeleteMenu = State()

# Ambil gambar menu dari API
urlgmenu = f"{API_BASE_URL}/restoran/image"
body = {"idRestoran": RESTAURANT_ID}
responsegmenu = requests.post(urlgmenu, json=body)

if responsegmenu.status_code == 200:
    dataMenu = json.loads(responsegmenu.text)
    link = dataMenu['data']
    print(link)
    gambar = open(f"c:\Skripsi\skripsi-api\image\{link}", 'rb')
    print(gambar)
else:
    print(f"Error: {responsegmenu.status_code}")
    print(f"Error: {responsegmenu.text}")

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

## Barisan tombol-tombol
buttonCancel = KeyboardButton("cancel")
buttonEdit = KeyboardButton("edit")
buttonsudah = KeyboardButton("sudah")
buttonDelete = KeyboardButton("delete")
buttonTidakJadi = KeyboardButton("tidak jadi")

keyboardmenu = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True).add(
    *[KeyboardButton(item) for item in menu_items],
    buttonEdit,
    buttonDelete,
    buttonCancel,
    buttonsudah
)

## Tombol edit menu pesanan
keyboardmenuedit = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True).add(
    *[KeyboardButton(item) for item in menu_items]
)

## Tombol delete menu pesanan
keyboardDeleteMenu = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True).add(
    *[KeyboardButton(item) for item in menu_items],
    buttonTidakJadi
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
    username = message.from_user.username
    if username is None:
        username = message.from_user.first_name
    try:
        logger.info(f"User {username} memulai chat")
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
        await message.answer("Ini untuk menunya ya kak. Silahkan dipilih")
    except Exception as e:
        traceback.print_exc()
        error_message = "Terjadi kesalahan saat menampilkan menu"
        await message.answer(error_message)

### Menampilkan Info lewat commands di NLP Mode
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
        await MyStates.awalPesan.set()
        await message.answer(pesan_answer, reply_markup=keyboardnomeja)
    except Exception as e:
        traceback.print_exc()
        error_message = "Terjadi kesalahan saat memulai pemesanan"
        await message.answer(error_message)

varTransaksi = ""

### Fungsi tombol input nomor meja
@dp.message_handler(state=MyStates.awalPesan)
async def input_table_number(message: types.Message, state: FSMContext):
    username = message.from_user.username
    if username is None:
        username = message.from_user.first_name
    logger.info(f"User {username} memilih nomor meja {message.text}")
    urlmeja = f"{API_BASE_URL}/transaksi/postTransaksi"
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
        await state.set_state(state=MyStates.awalPesan)
        print(f"Error: {responsemeja.status_code}")
        print(f"Error: {responsemeja.text}")
    
    meja_response = f"Oke, kamu di meja nomor {nomorMeja} ya, tekan tombol /menu ini untuk menampilkan menunya atau ketik apapun untuk lanjut ke langkah selanjutnya"
    await MyStates.tampilMenu.set()
    await message.reply(meja_response)

### Menampilkan Menu lewat state
@dp.message_handler(state=MyStates.tampilMenu)
async def show_menu_state(message: types.Message, state: FSMContext):
    with open(f"C:\Skripsi\skripsi-api\image\{link}", 'rb') as photo:
        await bot.send_photo(message.chat.id, photo)
    await MyStates.inputPesanan.set()
    await message.answer("Ini untuk menunya ya kak, mau pesan apa? Silahkan tekan tombol yang tersedia ya kak", reply_markup=keyboardmenu)

varidmenu = ""

### Fungsi tombol input menu pesanan
@dp.message_handler(state=MyStates.inputPesanan)
async def input_order_menu(message: types.Message, state: FSMContext):
    username = message.from_user.username
    if username is None:
        username = message.from_user.first_name
    logger.info(f"User {username} memesan menu {message.text}")
    global varTransaksi
    global varidmenu
    idTransaksi = varTransaksi
    print("Ini idTransaksi: ", idTransaksi)

    urlgetdetail = f"{API_BASE_URL}/transaksi/getDetailTransaksi"
    bodygetdetail = {
            "idTransaksi": varTransaksi
        }
    responsegetdetail = requests.post(urlgetdetail, json=bodygetdetail)
    if responsegetdetail.status_code == 200:
        datagetdetail = json.loads(responsegetdetail.text)
        print(datagetdetail) 
    else:
        print(f"Error: {responsegetdetail.status_code}")
        print(f"Error: {responsegetdetail.text}")

    if message.text in menu_items:
        namaMenu = message.text

        res = data["data"]
        for r in res:
            if r["nama"] == message.text:
                varidmenu = r["idMenu"]
                print("Ini idMenu: ", varidmenu)
                break

        await MyStates.orderQty.set()
        await message.reply(f"Kamu pesan {namaMenu} ya kak, mau berapa porsi nih?", reply_markup=keyboardjmlmenu)
    elif message.text == "edit":
        await MyStates.editPesanan.set()
        await message.answer("Menu mana kak yang mau di edit?", reply_markup=keyboardmenuedit)
    elif message.text == "delete":
        await MyStates.deleteMenu.set()
        await message.answer("Menu mana kak yang mau di delete?", reply_markup=keyboardDeleteMenu)
    elif message.text == "cancel":
        if varTransaksi is not None:
            urlcancel = f"{API_BASE_URL}/transaksi/cancel"
            bodycancel = {
                    "idTransaksi": varTransaksi,
                    "username": username
                }
            responsecancel = requests.post(urlcancel, json=bodycancel)
            if responsecancel.status_code == 200:
                datacancel = json.loads(responsecancel.text)
                print(datacancel) 
            else:
                print(f"Error: {responsecancel.status_code}")
                print(f"Error: {responsecancel.text}")
            await state.finish()
            await message.answer("Kamu sudah mengcancel pesanan kamu ya. Klik /pesan untuk memesan kembali. Btw kamu sekarang ada di Mode Chatting ya")
        else:
            await state.finish()
            await message.answer("Oke kak tapi kamu belom ada transaksi apapun. Klik /pesan kalo mau pesan sesuatu ya kak")
    elif message.text == "sudah":
        await state.finish()
        sudahAnswer = f"Oke kak siap terima kasih ini notanya ya, silahkan ke kasir untuk membayar\n\nID Pelanggan: {username}\nID Transaksi: {idTransaksi}\n\n"
        for item in datagetdetail['data']:
            # idMenu = item["idMenu"] #Belom tau dibutuhin apa gak
            nama = item["nama"]
            qty = item["qty"]
            harga = item["harga"]
            subHarga = item["subHarga"]

            item_text = f"Nama: {nama}\nQty: {qty}\nHarga: {harga:,}\nSubharga: {subHarga:,}\n\n"
            sudahAnswer += item_text

        sudahAnswer += f"Total: {datagetdetail['total']:,}"
        print(idTransaksi)
        print(sudahAnswer)
        await message.reply(sudahAnswer)
        await message.answer("Kamu sudah kembali ke Mode Chatting lagi ya. Kalo ada yang mau ditanyain tanya aja")
    else:
        await state.set_state(state=MyStates.inputPesanan)
        await message.answer("Maaf kak menunya hanya yang ada di tombol saja ya. Jadi mau pesan apa nih kak?", reply_markup=keyboardmenu)

varidDetail = ""

### Fungsi tombol edit pesanan
@dp.message_handler(state=MyStates.editPesanan)
async def edit_order_menu(message: types.Message, state: FSMContext):
    username = message.from_user.username
    if username is None:
        username = message.from_user.first_name
    logger.info(f"User {username} meminta untuk edit pesanan {message.text}")
    global varTransaksi
    global varidmenu
    global varidDetail
    await message.answer("Oke siap kak!")
    idTransaksi = varTransaksi
    print("Ini idTransaksi: ", idTransaksi)

    ## Fungsi edit pesanan
    urlnota = f"{API_BASE_URL}/transaksi/getDetailTransaksi"
    bodyNota = {"idTransaksi": varTransaksi}

    responsenota = requests.post(urlnota, json=bodyNota)
    dataNota = json.loads(responsenota.text)
    itemNota = [item['nama'] for item in dataNota['data']]

    urlgetdetail = f"{API_BASE_URL}/transaksi/getDetailTransaksi"
    bodygetdetail = {
            "idTransaksi": varTransaksi
        }
    responsegetdetail = requests.post(urlgetdetail, json=bodygetdetail)
    if responsegetdetail.status_code == 200:
        datagetdetail = json.loads(responsegetdetail.text)
        print(datagetdetail) 
    else:
        print(f"Error: {responsegetdetail.status_code}")
        print(f"Error: {responsegetdetail.text}")

    if message.text in itemNota:
        namaMenu = message.text

        res = datagetdetail["data"]
        for r in res:
            if r["nama"] == message.text:
                varidDetail = r["idDetailTransaksi"]
                print("Ini idDetailTransaksi: ", varidDetail)
                break

        await MyStates.inputEditPesanan.set()
        await message.reply(f"Kamu mau edit {namaMenu} jadi menu apa kak?", reply_markup=keyboardmenuedit)
    else:
        await state.set_state(state=MyStates.editPesanan)
        await message.answer("Maaf kak kamu belom pesen itu, Menu mana kak yang mau di edit?", reply_markup=keyboardmenuedit)

qty = ""

### Fungsi input edit pesanan
@dp.message_handler(state=MyStates.inputEditPesanan)
async def input_order_menu(message: types.Message, state: FSMContext):
    username = message.from_user.username
    if username is None:
        username = message.from_user.first_name
    logger.info(f"User {username} edit pesanan menjadi {message.text}")
    global varTransaksi
    global varidmenu
    global varidDetail
    global qty
    await message.answer("Oke siap kak!")
    idTransaksi = varTransaksi
    quantity = qty
    print("Ini idTransaksi: ", idTransaksi)

    urleditpesanan = f"{API_BASE_URL}/transaksi/editPesanan"
    bodyeditpesanan = {
            "idTransaksi": varTransaksi,
            "idDetailTransaksi": varidDetail,
            "idMenu": varidmenu,
            "qty": int(quantity)
        }
    responseeditpesanan = requests.post(urleditpesanan, json=bodyeditpesanan)
    if responseeditpesanan.status_code == 200:
        datagetdetail = json.loads(responseeditpesanan.text)
        print(datagetdetail) 
    else:
        print(f"Error: {responseeditpesanan.status_code}")
        print(f"Error: {responseeditpesanan.text}")

    if message.text in menu_items:
        namaMenu = message.text

        res = data["data"]
        for r in res:
            if r["nama"] == message.text:
                varidmenu = r["idMenu"]
                print("Ini idMenu: ", varidmenu)
                break

        await MyStates.qtyEditPesanan.set()
        await message.reply(f"Kamu pesan {namaMenu} ya kak, mau berapa porsi nih?", reply_markup=keyboardjmlmenu)
    else:
        await state.set_state(state=MyStates.inputEditPesanan)
        await message.reply(f"Maaf kak kamu salah input, Kamu mau edit {namaMenu} jadi menu apa kak?", reply_markup=keyboardmenuedit)

### Fungsi edit input jumlah menu pesanan
@dp.message_handler(state=MyStates.qtyEditPesanan)
async def input_order_quantity(message: types.Message, state: FSMContext):
    global varTransaksi
    global varidmenu
    global qty
    await message.answer("Okay siap kak!")
    idTransaksi = varTransaksi
    print("Ini idTransaksi: ", idTransaksi)

    if message.text in [str(i) for i in range(1, max_menu + 1)]:
        qty = message.text
        await state.set_state(state=MyStates.inputPesanan)
        await message.reply("Apakah ada yang mau dipesan lagi kak? Kalo udah silahkan tekan tombol sudahnya ya kak", reply_markup=keyboardmenu)
        idmenu = varidmenu
        quantity = qty
        urleditpesanan = f"{API_BASE_URL}/transaksi/editPesanan"
        bodyeditpesanan = {
                "idTransaksi": varTransaksi,
                "idDetailTransaksi": varidDetail,
                "idMenu": idmenu,
                "qty": int(quantity)
            }
        responseeditpesanan = requests.post(urleditpesanan, json=bodyeditpesanan)
        if responseeditpesanan.status_code == 200:
            datagetdetail = json.loads(responseeditpesanan.text)
            print(datagetdetail) 
        else:
            print(f"Error: {responseeditpesanan.status_code}")
            print(f"Error: {responseeditpesanan.text}")
        
        urlgetdetail = f"{API_BASE_URL}/transaksi/getDetailTransaksi"
        bodygetdetail = {
                "idTransaksi": varTransaksi
            }
        responsegetdetail = requests.post(urlgetdetail, json=bodygetdetail)
        if responsegetdetail.status_code == 200:
            datagetdetail = json.loads(responsegetdetail.text)
            print(datagetdetail) 
        else:
            print(f"Error: {responsegetdetail.status_code}")
            print(f"Error: {responsegetdetail.text}")
        noteAnswer = "**\n\n"
        for item in datagetdetail['data']:
            # idMenu = item["idMenu"] #Belom tau dibutuhin apa gak
            nama = item["nama"]
            qty = item["qty"]
            harga = item["harga"]
            subHarga = item["subHarga"]

            item_text = f"Nama: {nama}\nQty: {qty}\nHarga: {harga:,}\nSubharga: {subHarga:,}\n\n"
            noteAnswer += item_text

        noteAnswer += f"Total: {datagetdetail['total']:,}"
        print(idTransaksi)
        print(noteAnswer)
        await message.answer(noteAnswer)
    else:
        await state.set_state(state=MyStates.qtyEditPesanan)
        await message.reply(f"Maaf kak mau berapa porsi nih?", reply_markup=keyboardjmlmenu)

### Fungsi input jumlah menu pesanan
@dp.message_handler(state=MyStates.orderQty)
async def input_order_quantity(message: types.Message, state: FSMContext):
    global varTransaksi
    global varidmenu
    global qty
    await message.answer("Okay siap kak!")
    idTransaksi = varTransaksi
    print("Ini idTransaksi: ", idTransaksi)

    if message.text in [str(i) for i in range(1, max_menu + 1)]:
        qty = message.text
        await state.set_state(state=MyStates.inputPesanan)
        await message.reply("Apakah ada yang mau dipesan lagi kak? Kalo udah silahkan tekan tombol sudahnya ya kak", reply_markup=keyboardmenu)

        urlpesan = f"{API_BASE_URL}/transaksi/postPesanan"
        idtransaksi = idTransaksi
        idmenu = varidmenu
        quantity = qty

        bodypesan = {
            "idTransaksi": idtransaksi,
            "idMenu": int(idmenu),
            "qty": int(quantity)
        }

        responsepesan = requests.post(urlpesan, json=bodypesan)
        if responsepesan.status_code == 200:
            datapesan = json.loads(responsepesan.text)
            print(datapesan) 
        else:
            print(f"Error: {responsepesan.status_code}")
            print(f"Error: {responsepesan.text}")
        
        urlgetdetail = f"{API_BASE_URL}/transaksi/getDetailTransaksi"
        bodygetdetail = {
                "idTransaksi": varTransaksi
            }
        responsegetdetail = requests.post(urlgetdetail, json=bodygetdetail)
        if responsegetdetail.status_code == 200:
            datagetdetail = json.loads(responsegetdetail.text)
            print(datagetdetail) 
        else:
            print(f"Error: {responsegetdetail.status_code}")
            print(f"Error: {responsegetdetail.text}")
        noteAnswer = "**\n\n"
        for item in datagetdetail['data']:
            # idMenu = item["idMenu"] #Belom tau dibutuhin apa gak
            nama = item["nama"]
            qty = item["qty"]
            harga = item["harga"]
            subHarga = item["subHarga"]

            item_text = f"Nama: {nama}\nQty: {qty}\nHarga: {harga:,}\nSubharga: {subHarga:,}\n\n"
            noteAnswer += item_text

        noteAnswer += f"Total: {datagetdetail['total']:,}"
        print(idTransaksi)
        print(noteAnswer)
        await message.answer(noteAnswer)
    else:
        await state.set_state(state=MyStates.orderQty)
        await message.reply(f"Maaf kak mau berapa porsi nih?", reply_markup=keyboardjmlmenu)

### Fungsi delete menu
@dp.message_handler(state=MyStates.deleteMenu)
async def input_order_menu(message: types.Message, state: FSMContext):
    username = message.from_user.username
    if username is None:
        username = message.from_user.first_name
    logger.info(f"User {username} ingin menghapus {message.text}")
    global varTransaksi
    # await message.answer("Oke siap kak!")
    idTransaksi = varTransaksi
    print("Ini idTransaksi: ", idTransaksi)

    urlgetdetail = f"{API_BASE_URL}/transaksi/getDetailTransaksi"
    bodygetdetail = {
            "idTransaksi": idTransaksi
        }
    
    responsegetdetail = requests.post(urlgetdetail, json=bodygetdetail)
    if responsegetdetail.status_code == 200:
        datagetdetail = json.loads(responsegetdetail.text)
    else:
        print(f"Error: {responsegetdetail.status_code}")
        print(f"Error: {responsegetdetail.text}")

    namaMenu = [item['nama'] for item in datagetdetail['data']]
    if message.text in namaMenu:
        res = datagetdetail["data"]
        for r in res:
            if r["nama"] == message.text:
                varidDetail = r["idDetailTransaksi"]
                print("Ini idDetailTransaksi: ", varidDetail)

                urlDelete = f"{API_BASE_URL}/transaksi/deleteDetailPesanan"
                bodyDelete = {
                        "idDetailTransaksi": varidDetail
                    }

                responseDelete = requests.post(urlDelete, json=bodyDelete)
                json.loads(responseDelete.text)
                break

        await state.set_state(state=MyStates.inputPesanan)
        await message.reply(f"Oke kak, kamu delete {message.text} ya kak. Mau pesen apa lagi nih?", reply_markup=keyboardmenu)
    elif message.text == "tidak jadi":
        await state.set_state(state=MyStates.inputPesanan)
        await message.reply(f"Oke kak siap. Mau pesen apa lagi nih?", reply_markup=keyboardmenu)
    else:
        await state.set_state(state=MyStates.deleteMenu)
        await message.reply(f"Maaf kak kamu salah input, Kamu mau delete menu yang mana kak?", reply_markup=keyboardDeleteMenu)

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