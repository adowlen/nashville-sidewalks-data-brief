# Composites the headline over generated art in hero_source/*.webp (first match).
# Parent generates the art after QA; run this once hero_source holds a .webp.
from PIL import Image, ImageDraw, ImageFont
import os, glob
PKG=os.path.normpath(os.path.join(os.path.dirname(__file__),".."))
def main():
    cands=sorted(glob.glob(os.path.join(PKG,"hero_source","*.webp")))
    if not cands: print("NO hero_source art yet - hero.png not created (expected pre-QA)"); return
    src=cands[0]; img=Image.open(src).convert("RGB"); W,H=img.size
    sh=int(H*0.42); scrim=Image.new("L",(1,sh),0)
    for y in range(sh): scrim.putpixel((0,y), int(215*(1-y/sh)))
    scrim=scrim.resize((W,sh)); black=Image.new("RGB",(W,sh),(18,18,18))
    img.paste(Image.composite(black, img.crop((0,0,W,sh)), scrim),(0,0))
    d=ImageDraw.Draw(img)
    def font(sz): return ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",sz)
    x=int(W*0.045)
    d.text((x,int(H*0.045)),"25.2%",font=font(int(H*0.115)),fill=(232,163,61))
    d.text((x,int(H*0.175)),"of Nashville's inventoried sidewalk segments are",font=font(int(H*0.038)),fill=(245,245,245))
    d.text((x,int(H*0.225)),"recorded Fair or Poor - 1,454 of them Poor",font=font(int(H*0.038)),fill=(245,245,245))
    d.text((x,int(H*0.295)),"Metro Nashville Sidewalks Inventory - 14,938 segments pulled Nov 10, 2026  |  Machine Readable",font=font(int(H*0.020)),fill=(180,220,215))
    img.save(os.path.join(PKG,"hero.png")); print("hero.png",img.size,"from",src)
if __name__=="__main__": main()
