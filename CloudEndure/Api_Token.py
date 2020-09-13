import requests
import json

Url = "https://console.cloudendure.com/api/latest/login"
Object = {
    "username": "cloudenduredr@nbaysolutions.net",
    "password": "Likh&876V$#@"
}
res = requests.post(Url, json=Object)
res_object = json.loads(res.text)
print(res_object['apiToken'])