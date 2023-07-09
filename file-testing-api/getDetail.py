import requests
import json

urlgetdetail = "http://localhost:3000/transaksi/getDetailTransaksi"

bodygetdetail = {
            "idTransaksi": 155
        }

responsegetdetail = requests.post(urlgetdetail, json=bodygetdetail)
if responsegetdetail.status_code == 200:
    datagetdetail = json.loads(responsegetdetail.text)
    print(datagetdetail['data']) 
else:
    print(f"Error: {responsegetdetail.status_code}")
    print(f"Error: {responsegetdetail.text}")
## Print nota total
sudahAnswer = "Oke kak siap terima kasih ini notanya ya, silahkan ke kasir untuk membayar\n\n"
for item in datagetdetail['data']:
    idMenu = item["idMenu"]
    nama = item["nama"]
    qty = item["qty"]
    harga = item["harga"]
    subHarga = item["subHarga"]

    item_text = f"ID Menu: {idMenu}\nNama: {nama}\nQty: {qty}\nHarga: {harga:,}\nSubharga: {subHarga:,}\n\n"
    sudahAnswer += item_text

sudahAnswer += f"Total: {datagetdetail['total']:,}"
print(sudahAnswer)

## Untuk dapat idDetailTransaksi by nama menu
message = input(">> ")
namaMenu = [item['nama'] for item in datagetdetail['data']]
if message in namaMenu:
        nama_menu = message

        res = datagetdetail["data"]
        for r in res:
            if r["nama"] == message:
                varidDetail = r["idDetailTransaksi"]
                print("Ini idDetailTransaksi: ", varidDetail)
                break
    