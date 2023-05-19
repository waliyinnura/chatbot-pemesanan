import requests
import json
import pprint

urlpatterns = "http://localhost:3000/patterns/intents"
body = {"idRestoran":28}

responsepatterns = requests.post(urlpatterns, json=body)

if responsepatterns.status_code == 200:
    data = json.loads(responsepatterns.text)
    print(data)
    # name = data['name']
    # premiered = data['premiered']
    # summary = data['summary']
    # href = data['_links']['self']['href']
    # print(f"{name} premiered on {premiered}.")
    # print(summary)
    # print(href)   
else:
    print(f"Error: {responsepatterns.status_code}")
    print(f"Error: {responsepatterns.text}")

