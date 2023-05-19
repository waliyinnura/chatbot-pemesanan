import requests
import json

urlpesan = "http://localhost:3000/transaksi/postPesanan"
idtransaksi = 27
idmenu = 29
quantity = 1

body = {
    "idTransaksi": idtransaksi,
    "idMenu": idmenu,
    "qty": quantity
    }

responsepesan = requests.post(urlpesan, json=body)

if responsepesan.status_code == 200:
    data = json.loads(responsepesan.text)
    print(data)  
else:
    print(f"Error: {responsepesan.text}")
    print(f"Error: {responsepesan.status_code}")
