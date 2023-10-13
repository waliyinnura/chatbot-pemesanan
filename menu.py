import requests
from PIL import Image
from io import BytesIO
import pprint
import json

urlmenu = "http://localhost:3000/restoran/image"
body = {"idRestoran":29}

responsemenu = requests.post(urlmenu, json=body)

if responsemenu.status_code == 200:
    data = json.loads(responsemenu.text)
    link = data['data']
    print(link)
    gambar = open(f"C:\Skripsi\skripsi-api\image\{link}", 'rb')
    print(gambar)
else:
    print(f"Error: {responsemenu.status_code}")
    print(f"Error: {responsemenu.text}")