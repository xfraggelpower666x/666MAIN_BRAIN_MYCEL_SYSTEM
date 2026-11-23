#!/usr/bin/env python3
import argparse
import json
import qrcode

parser = argparse.ArgumentParser(description="generate 3DXChat world from QR code")
parser.add_argument("url")
parser.add_argument("-r", "--resize", type=float, default=1.0)
parser.add_argument("-o", "--output_file", default="")
args = parser.parse_args()
if args.resize <= 0:
    parser.error("resize must be greater than zero")
qr = qrcode.QRCode(border=4)
qr.add_data(args.url)
qr.make(fit=True)
world = {"respawn":{"p":[0.,1.,-5.],"r":180.},"ambient":[1.]*9,"oceanlevel":0.,"weather":"Day","valuetype":"float","objects":[{"n":"group","objects":[]}]}
for y,row in enumerate(qr.get_matrix()):
    for x,dark in enumerate(row):
        if dark:
            world["objects"][0]["objects"].append({"n":"Box","p":[x*args.resize,y*args.resize,0.],"r":[0.,0.,0.],"s":[args.resize,args.resize,0.1],"c":[0.,0.,0.],"m":"unlit"})
output=json.dumps(world)
if args.output_file:
    with open(args.output_file,"w",encoding="utf-8") as f:
        f.write(output)
else:
    print(world)
