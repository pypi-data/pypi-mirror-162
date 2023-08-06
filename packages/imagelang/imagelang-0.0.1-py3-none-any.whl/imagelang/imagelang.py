######### biar exec bisa sukses
import cv2
from urllib.request import urlopen
import numpy as np
import os, sys
from pprint import pprint as pp
from uuid import uuid4 as u4


mapwarna = {
    "blue": (255, 0, 0),
    "green": (0, 255, 0),
    "red": (0, 0, 255),
    "cyan": (255, 255, 0),
    "magenta": (255, 0, 255),
    "yellow": (0, 255, 255),
    "white": (255, 255, 255),
    "black": (0, 0, 0),
}

# enum HersheyFonts {
#     FONT_HERSHEY_SIMPLEX        = 0, //!< normal size sans-serif font
#     FONT_HERSHEY_PLAIN          = 1, //!< small size sans-serif font
#     FONT_HERSHEY_DUPLEX         = 2, //!< normal size sans-serif font (more complex than FONT_HERSHEY_SIMPLEX)
#     FONT_HERSHEY_COMPLEX        = 3, //!< normal size serif font
#     FONT_HERSHEY_TRIPLEX        = 4, //!< normal size serif font (more complex than FONT_HERSHEY_COMPLEX)
#     FONT_HERSHEY_COMPLEX_SMALL  = 5, //!< smaller version of FONT_HERSHEY_COMPLEX
#     FONT_HERSHEY_SCRIPT_SIMPLEX = 6, //!< hand-writing style font
#     FONT_HERSHEY_SCRIPT_COMPLEX = 7, //!< more complex variant of FONT_HERSHEY_SCRIPT_SIMPLEX
#     FONT_ITALIC                 = 16 //!< flag for italic font
# };

font = cv2.FONT_HERSHEY_PLAIN
#########

from declang.processor import process_language
from langutils.app.printutils import indah4
from langutils.app.treeutils import (
    anak,
    data,
    token,
    child1,
    child2,
    child3,
    child4,
    child,
    chdata,
    chtoken,
    ispohon,
    istoken,
    beranak,
    sebanyak,
    jumlahanak,
)
from langutils.app.dirutils import joiner
from langutils.app.fileutils import file_write
from langutils.app.utils import env_get


imgoutput = {}


def reset():
    global imgoutput
    imgoutput.clear()


def imghandler(tree, parent=""):
    kembali = ""
    name, attrs, children, text = "", "", "", ""
    namaparent = ""
    itemid = ""
    for item in anak(tree):
        jenis = data(item)
        if jenis == "element_name":
            namaparent = token(item)
            itemid = str(u4())
            print("elem:", namaparent)
            if namaparent == "canvas":
                print("tag canvas")
                imgoutput["canvas"] = {}
            elif namaparent == "img":
                print("tag img", "parent:", parent)
            elif namaparent == "text":
                print("tag text", "parent:", parent)
        elif jenis == "element_config":
            for tupleitem in anak(item):
                jenis2 = data(tupleitem)
                if jenis2 == "item_key_value":
                    k, v = "", ""
                    for anaktupleitem in anak(tupleitem):
                        jenis3 = data(anaktupleitem)
                        if jenis3 == "item_key":
                            k = token(anaktupleitem)
                        elif jenis3 == "item_value":
                            v = token(anaktupleitem)
                    print(f"  attr {namaparent}/{itemid} k=v => {k}={v}")
                    if namaparent == "canvas":
                        if k == "w":
                            imgoutput["width"] = v
                        elif k == "h":
                            imgoutput["height"] = v
                        elif k == "color":
                            imgoutput["color"] = v
                    else:
                        print(f"adding {k}={v}", end="")
                        if not itemid in imgoutput["canvas"]:
                            print(f" to new {namaparent}")
                            imgoutput["canvas"][itemid] = {
                                "type": namaparent,
                                "attrs": [f"{k}={v}"],
                            }
                        else:
                            print(f" to existing {namaparent}")
                            # attrs = imgoutput['canvas'][itemid]['attrs'].append(f"{k}={v}")
                            # imgoutput['canvas'][itemid]['attrs'] = attrs
                            imgoutput["canvas"][itemid]["attrs"].append(f"{k}={v}")
                elif jenis2 == "item_key_value_boolean":
                    nilai = token(tupleitem)
                    print(f"  attr {namaparent}/{itemid} bool => {nilai}")
        elif jenis == "element_children":
            for tupleitem in anak(item):
                for anaktupleitem in tupleitem:
                    res = imghandler(anaktupleitem, parent=namaparent)
        elif jenis == "cdata_text":
            text = token(item)
            print(f"  cdata {namaparent}/{itemid}:", text)
            if itemid not in imgoutput["canvas"]:
                # ini jk kita tdk specify config [], hanya cdata
                # tapi masih gagal nih
                # ../img)<canvas(<img[src=U//bali]<text|this is my first journey)
                # oh ternyata muncul, tapi kepotong, ada di atas...
                # create_text(0,0,"hello world","black")
                imgoutput["canvas"][itemid] = {"attrs": [], "type": "text"}
            imgoutput["canvas"][itemid]["attrs"].append(f"text={text}")


kode_output_image = """
import numpy as np
import cv2
import random
import requests
from urllib.request import urlopen

mapwarna = {
    'blue': (255,0,0),
    'green': (0,255,0),
    'red': (0,0,255),

    'cyan': (255,255,0),
    'magenta': (255,0,255),
    'yellow': (0,255,255),

    'white': (255,255,255),
    'black': (0,0,0),
}

font = cv2.FONT_HERSHEY_PLAIN
img = np.zeros((__LEBAR__, __TINGGI__, 3), dtype=np.uint8)
#img.fill(__WARNA__) # or img[:] = 255
img[:] = __WARNA__

def create_rect(x,y,w,h,warna='red'):
    # global img
    x,y,w,h = int(x),int(y),int(w),int(h)
    cv2.rectangle(img, (x,y), (x+w,y+h), mapwarna[warna], -1)

def create_circle(x,y,w,h,warna='red'):
    # global img
    center = (x+(w//2), y+(h//2))
    radius = min(w,h)//2
    cv2.circle(img, center, radius, mapwarna[warna], -1)

def create_eclipse(x,y,w,h,warna='red'):
    # global img
    center = (x+(w//2), y+(h//2))
    radius = min(w,h)//2
    ax1 = w//2
    ax2 = h//2
    angle = 0
    startangle = 0
    endangle = 360
    cv2.eclipse(img, center, (ax1,ax2), angle, startangle, endangle, mapwarna[warna], -1)

def create_image(alamat, x,y,w,h, alpha=0.5):
    global img
    x,y,w,h = int(x),int(y),int(w),int(h)
    req = urlopen(alamat)
    #print(alamat, ':', req)
    image = np.asarray(bytearray(req.read()), dtype=np.uint8)
    #image = cv2.imdecode(image, -1)
    image = cv2.imdecode(image, cv2.IMREAD_COLOR)
    if w==0 or h==0:
        h,w,_=image.shape
    else:
        image = cv2.resize(image.copy(), (w,h))
    #img = np.uint8(img*alpha + image*(1-alpha))
    #print(f'''
    #x = {x}
    #y = {y}
    #w = {w}
    #    x+w = {x+w}
    #h = {h}
    #    y+h = {y+h}
    #shape 1 = {img.shape}
    #shape 2 = {image.shape}
    #''')
    #https://stackoverflow.com/questions/56002672/display-an-image-over-another-image-at-a-particular-co-ordinates-in-opencv
    #img[x:x+w,y:y+h,:] = image[0:w,0:h,:]
    img[y:y+image.shape[0], x:x+image.shape[1]] = image

def create_line():
    pass

def create_text(x, y, tulisan, warna='black', scale=1.5, thick=2):
    # (image, text, org, font, fontScale, color[, thickness[, lineType[, bottomLeftOrigin]]])
    x,y = int(x),int(y)
    if y == 0:
        y = 25 # biar keliatan
    cv2.putText(img, tulisan, (x,y), font, scale, mapwarna[warna], thick)

__TEMPLATE_CODE__

cv2.imshow('gambar', img)
cv2.waitKey(0)
cv2.destroyAllWindows()
"""


# unsplash
# unsplash/w,h
# unsplash/w,h/wallpaper,landscape
# picsum -> 640x480
# picsum/w,h
# https://source.unsplash.com/random/1920x1080/?wallpaper,landscape
# https://source.unsplash.com/random/1920x1080
# https://source.unsplash.com/random
# https://picsum.photos/1920/1080


def process_output(imgoutput):
    template_codes = []
    # pastikan background size > ukuran image yg akan didownload
    screen_width = "2000"
    screen_height = "2000"  # 1920x1080, 1920 kenapa jadi tinggi?
    screen_background = "white"

    if "width" in imgoutput:
        screen_width = imgoutput["width"]
    if "height" in imgoutput:
        screen_height = imgoutput["height"]
    if "color" in imgoutput:
        screen_background = imgoutput["color"]

    for k, v in imgoutput.items():
        if k == "canvas":
            for l, w in imgoutput["canvas"].items():
                print(f"oprek {l} dan {w}/{type(w)}")
                if w["type"] == "img":
                    x, y, width, height, alpha = 0, 0, 0, 0, 0.9
                    fungsi = "create_rect"
                    alamat = ""
                    warna = "red"
                    # print(f'sekali lagi, w adlh: {w} jenis {type(w)}')
                    # print(f'sekali lagi, w adlh: {w} dan attrs nya adlh {w["attrs"]}')
                    for anaklaki in w["attrs"]:
                        # print(f'oprek anaklaki {anaklaki}')
                        kunci, nilai = anaklaki.split("=", 1)
                        if kunci == "x":
                            x = float(nilai)
                            if nilai.startswith("."):
                                x = float(nilai) * float(screen_width)
                                # print(f"bangsat float(nilai)*float(screen_width) = float(nilai)*float(screen_width) = ")
                            indah4(
                                f"nilai {nilai}, x {x}, sw = {screen_width}",
                                warna="blue",
                            )
                        elif kunci == "y":
                            if nilai.startswith("."):
                                y = float(nilai) * float(screen_height)
                            else:
                                y = float(nilai)
                            indah4(
                                f"nilai {nilai}, y {y}, sh = {screen_height}",
                                warna="blue",
                            )
                        elif kunci == "w":
                            if nilai.startswith("."):
                                width = float(nilai) * float(screen_width)
                            else:
                                width = int(nilai)
                            indah4(
                                f"nilai {nilai}, width {width}, sw = {screen_width}",
                                warna="blue",
                            )
                        elif kunci == "h":
                            if nilai.startswith("."):
                                height = float(nilai) * float(
                                    screen_height
                                )  # .25 => 25% height
                            else:
                                height = int(nilai)
                            indah4(
                                f"nilai {nilai}, height {height}, sh = {screen_height}",
                                warna="blue",
                            )
                        elif kunci == "alpha":
                            if nilai.startswith("."):
                                alpha = float(nilai)
                            else:
                                alpha = float(nilai) / 100  # 80 -> 0.8
                        elif kunci == "color":
                            warna = nilai
                        elif kunci == "src":
                            if (
                                nilai.startswith("http")
                                or nilai.startswith("U")
                                or nilai.startswith("P")
                            ):
                                fungsi = "create_image"
                                alamat = nilai
                            elif nilai in ["rect", "circle", "ellipse", "line"]:
                                fungsi = "create_" + nilai
                    # generate
                    if fungsi == "create_image":
                        if alamat.startswith("U"):
                            alamat = alamat.removeprefix("U")
                            if not alamat:
                                alamat = "https://source.unsplash.com/random"
                            elif alamat.count("/") == 2:
                                # U/1920x1080/wallpaper,landscape <- gak bisa comma
                                # U//wallpaper,landscape <- gak bisa comma
                                # https://source.unsplash.com/random/1920x1080/?wallpaper,landscape <- gak bisa comma
                                _, size, topic = alamat.split("/")
                                if not size:
                                    width = 640
                                    height = 480
                                else:
                                    # gak bisa comma, krn jadi item config yg berbeda dalam decl-lang
                                    width, height = size.split("x")
                                if topic:
                                    alamat = f"https://source.unsplash.com/random/{width}x{height}/?{topic}"
                                else:
                                    alamat = f"https://source.unsplash.com/random/{width}x{height}"
                            else:
                                # https://source.unsplash.com/random/1920x1080
                                if not width:
                                    width = 640
                                if not height:
                                    height = 480
                                alamat = f"https://source.unsplash.com/random/{width}x{height}"
                        if alamat.startswith("P"):
                            alamat = alamat.removeprefix("P")
                            # P
                            # P/1920x1080
                            if not alamat:
                                width = 640
                                height = 480
                            else:
                                _, alamat = alamat.split("/", 1)
                                width, height = alamat.split("x")
                            alamat = f"https://picsum.photos/{width}/{height}"
                        kode = (
                            f'{fungsi}("{alamat}", {x},{y},{width},{height}, {alpha})'
                        )
                    else:
                        kode = f'{fungsi}({x},{y},{width},{height},"{warna}")'
                    # indah4(kode, warna='green')
                elif w["type"] == "text":
                    x, y = 0, 0
                    scale = 1.0
                    warna = "black"
                    content = ""
                    for anaklaki in w["attrs"]:
                        kunci, nilai = anaklaki.split("=")
                        if kunci == "x":
                            x = float(nilai)
                            if nilai.startswith("."):
                                x = float(nilai) * float(screen_width)
                        elif kunci == "y":
                            if nilai.startswith("."):
                                y = float(nilai) * float(screen_height)
                            else:
                                y = float(nilai)
                        elif kunci == "color":
                            warna = nilai
                        elif kunci == "text":
                            content = nilai
                        elif kunci == "size" or kunci == "sz" or kunci == "z":
                            scale = nilai
                    kode = f'create_text({x},{y},"{content}","{warna}",{scale})'
                    indah4(kode, warna="yellow")
                template_codes.append(kode)

    content = kode_output_image.replace(
        "__TEMPLATE_CODE__", "\n\n".join(template_codes)
    )
    content = content.replace("__TINGGI__", screen_height).replace(
        "__LEBAR__", screen_width
    )
    content = content.replace("__WARNA__", f'mapwarna["{screen_background}"]')
    # file_output = joiner(env_get('ULIBPY_DATA_FOLDER_ABS'), 'gambar.py')
    # indah4(f'{file_output}',warna='cyan')
    # file_write(file_output, content)
    # indah4(f"kita mau exec [{content}]", warna='red')
    exec(content)


# image harus rectangular...
imgcode = """
<canvas[w=1000,h=800,color=red](
    <img[x=100,y=500,w=.25,h=.25,rotateccw=45,grayscale=50,alpha=80,src=rect,color=yellow]
    <img[x=10,y=150,w=500,h=600,src=https://i.pinimg.com/originals/33/32/6d/33326dcddbf15c56d631e374b62338dc.jpg]
    <text[x=10,y=250,sz=14,color=blue]|hello mama mia di tinggi 250
    <text[x=10,y=500,sz=14,color=green]|ini di tinggi 500
)
"""


def imagelang(code=imgcode):
    reset()
    process_language(code, current_handler=imghandler)
    pp(imgoutput)
    process_output(imgoutput)
