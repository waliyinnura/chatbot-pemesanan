import requests
import json

#urlmenu = "http://localhost:3000/menu/getAllMenuIdRestoran"
#body = {"idRestoran": 28}
#responsemenu = requests.post(urlmenu, json=body)
#
#if responsemenu.ok:
#    data = json.loads(responsemenu.text)["data"]
#    res = [menu for menu in data if menu["nama"] == "mie goreng"]
#
#    if res:
#        idmenu = res[0]["idMenu"]
#        print(idmenu)
#    else:
#        print("Menu not found.")
#else:
#    print(f"Error: {responsemenu.status_code}")
#    print(f"Error: {responsemenu.text}")

## Dynamic response nya
# menu_items = {
#     "nasi goreng": "Kamu pesan nasi goreng, mau berapa porsi?",
#     "mie goreng": "Kamu pesan mie goreng, mau berapa porsi kak?",
#     "mie rebus": "Kamu pesan mie rebus, mau berapa porsi kak?"
# }

# if message.text in menu_items:
#     data = json.loads(responsemenu.text)
#     res = data["data"]
#     for r in res:
#         if r["nama"] == message.text:
#             varidmenu = r["idMenu"]
#             print("Ini idMenu: ", varidmenu)
#     await MyStates.FOURTH_STATE.set()
#     await message.reply(menu_items[message.text], reply_markup=keyboardjmlmenu)
#import json
#
## JSON data
#json_data = '''
#{
#    "data": [
#        {
#            "idMenu": 31,
#            "nama": "nasi goreng",
#            "tipe": "makanan",
#            "harga": 5000,
#            "tanggalBuat": "2023-06-12T10:00:49.000Z",
#            "tanggalUbah": "2023-06-12T10:00:49.000Z",
#            "idRestoran": 29
#        },
#        {
#            "idMenu": 32,
#            "nama": "mie goreng",
#            "tipe": "makanan",
#            "harga": 5000,
#            "tanggalBuat": "2023-06-12T10:01:03.000Z",
#            "tanggalUbah": "2023-06-12T10:01:03.000Z",
#            "idRestoran": 29
#        },
#        {
#            "idMenu": 33,
#            "nama": "mie rebus",
#            "tipe": "makanan",
#            "harga": 5000,
#            "tanggalBuat": "2023-06-12T10:01:41.000Z",
#            "tanggalUbah": "2023-06-12T10:01:41.000Z",
#            "idRestoran": 29
#        }
#    ]
#}
#'''
#urlmenu = "http://localhost:3000/menu/getAllMenuIdRestoran"
#body = {"idRestoran": 29}
#responsemenu = requests.post(urlmenu, json=body)
#data = json.loads(responsemenu.text)
## Parse JSON data
##data = json.loads(json_data)
#
## Get the 'nama' values
#menu_items = [item['nama'] for item in data['data']]
#print(menu_items)
#
## Create keyboardmenu dynamically
#keyboardmenu = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
#
#for item in menu_items:
#    print(item)
#    button = KeyboardButton(f"'{item}'")
#    print(button)
#    #keyboardmenu.add(button)

urlmenu = "http://localhost:3000/menu/getAllMenuIdRestoran"
body = {"idRestoran":29}
responsemenu = requests.post(urlmenu, json=body)
data = json.loads(responsemenu.text)
menu_items = [item['nama'] for item in data['data']]
print(menu_items)
for item in menu_items:
    namaMenu = item
    print(namaMenu)