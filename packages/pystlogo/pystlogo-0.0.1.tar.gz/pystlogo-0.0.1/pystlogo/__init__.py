from .error import check_connection
import os
import random
from PIL import Image, ImageDraw, ImageFont, ImageFilter
from telegraph import upload_file

def logo(name):
    check_connection()
    try:
        TXTSTD = f"{name}"
        folder = "./resources/bgs"
        imgpath = random.choice(os.listdir(folder))
        bgfile = folder+'/'+imgpath
        folder2 = "./resources/animes"
        imgpath2 = random.choice(os.listdir(folder2))
        anmfile = folder2+'/'+imgpath2
        # open resources
        STDIMG = Image.open(bgfile)
        ANMIMG = Image.open(anmfile)
        FONTSTD = ImageFont.truetype("./resources/ROAD_RAGE.OTF", 170)
        x = STDIMG.width//2
        y = STDIMG.height//2
        STDIMG.paste(ANMIMG, ANMIMG)
        SHADOW = Image.new('RGBA', STDIMG.size)
        draw = ImageDraw.Draw(SHADOW)
        draw.text((640, 870), text=TXTSTD, fill='black', font=FONTSTD, anchor='mm', stroke_width=15, stroke_fill='black')
        SHADOW = SHADOW.filter(ImageFilter.BoxBlur(5))
        STDIMG.paste(SHADOW, SHADOW)
        EDITSTD = ImageDraw.Draw(STDIMG)
        EDITSTD.text((640, 870), TXTSTD, font=FONTSTD, anchor="mm", stroke_width=3, stroke_fill='black', fill='White')
        animestd = f'animebystd.jpg'
        STDIMG.save("animebystd.jpg")
        if os.path.exists(animestd):
           response = upload_file(animestd)
        os.remove(animestd)
        x = f"https://telegra.ph{response[0]}"
        info = {"logo" : x}
        return info
    except Exception as e:
        info = {"logo" : {e}}
        return info

