#!/usr/bin/env python3
import PIL.Image as I
import argparse
import json

parser=argparse.ArgumentParser(description="convert image to 3DXChat world")
parser.add_argument("filename")
parser.add_argument("-r","--resize",type=float,default=1.0)
parser.add_argument("-e","--element_size",type=float,default=0.02)
parser.add_argument("-o","--output_file",default="")
args=parser.parse_args()
if args.resize<=0 or args.element_size<=0:
    parser.error("resize and element_size must be positive")
image=I.open(args.filename).convert("RGB")
width=max(1,int(image.width/args.resize))
height=max(1,int(image.height/args.resize))
image=image.resize((width,height),I.Resampling.LANCZOS if hasattr(I,"Resampling") else I.LANCZOS)
world={"respawn":{"p":[0.,0.,-5.],"r":0.},"ambient":[1.]*9,"oceanlevel":0.,"weather":"Night","valuetype":"float","objects":[{"n":"group","objects":[]}]}
for ix in range(width):
    y=1.0+height*args.element_size
    for iy in range(height):
        pixel=image.getpixel((ix,iy))
        world["objects"][0]["objects"].append({"n":"Box","p":[ix*args.element_size,y,0.],"r":[0.,0.,0.],"s":[args.element_size,args.element_size,0.1],"c":[p/255.0 for p in pixel],"m":"unlit"})
        y-=args.element_size
output=json.dumps(world)
if args.output_file:
    with open(args.output_file,"w",encoding="utf-8") as f:
        f.write(output)
else:
    print(world)
