import json
import requests

urlmenu = "http://localhost:3000/restoran/jumlahMeja"
body = {"idRestoran": 29}
responsemenu = requests.post(urlmenu, json=body)
data= json.loads(responsemenu.text)
value = data['data'][0]['jumlahMeja']
print(value)