import requests
import json

urlmenu = "http://localhost:3000/menu/getAllMenuIdRestoran"
body = {"idRestoran": 28}
responsemenu = requests.post(urlmenu, json=body)

if responsemenu.ok:
    data = json.loads(responsemenu.text)["data"]
    res = [menu for menu in data if menu["nama"] == "mie goreng"]

    if res:
        idmenu = res[0]["idMenu"]
        print(idmenu)
    else:
        print("Menu not found.")
else:
    print(f"Error: {responsemenu.status_code}")
    print(f"Error: {responsemenu.text}")

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
