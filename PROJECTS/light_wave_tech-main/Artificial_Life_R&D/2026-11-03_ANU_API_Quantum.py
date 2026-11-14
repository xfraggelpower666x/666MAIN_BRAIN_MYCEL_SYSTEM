# not anymore binare are they?! like they used to be 2014-2015... 
# not sure if this is any good anymore as it all costs now... but..
# to document if need arises for up-to-date way to get these.

import json
import requests

QRN_URL = "https://api.quantumnumbers.anu.edu.au/"
QRN_KEY = "txxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx7"  # replace with your secret API-KEY

DTYPE = "uint8"  # uint8, uint16, hex8, hex16
LENGTH = 10  # between 1--1024
BLOCKSIZE = 1  # between 1--10. Only needed for hex8 and hex16

params = {"length": LENGTH, "type": DTYPE, "size": BLOCKSIZE}
headers = {"x-api-key": QRN_KEY}

response = requests.get(QRN_URL, headers=headers, params=params)

if response.status_code == 200:
    js = response.json()
    if js["success"] == True:
        print(js["data"])
    else:
        print(js["message"])

else:
    print(f"Got an unexpected status-code: {response.status_code}")
    print(response.text)
