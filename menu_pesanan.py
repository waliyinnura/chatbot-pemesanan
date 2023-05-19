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
