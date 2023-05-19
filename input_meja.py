import requests
import json


urlpesan = "http://localhost:3000/transaksi/postTransaksi"
username = "wika"
nomorMeja = "3"
body = {
    "username": username,
    "nomorMeja": int(nomorMeja),
    "idRestoran":28
    }

responsepesan = requests.post(urlpesan, json=body)

if responsepesan.status_code == 200:
    data = json.loads(responsepesan.text)
    print(data)
    # name = data['name']
    # premiered = data['premiered']
    # summary = data['summary']
    # href = data['_links']['self']['href']
    # print(f"{name} premiered on {premiered}.")
    # print(summary)
    # print(href)   
else:
    print(f"Error: {responsepesan.status_code}")
    print(f"Error: {responsepesan.text}")