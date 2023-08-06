# -*- coding: utf-8 -*-
import io
import re
import base64
import numpy as np
from PIL import Image, ExifTags, ImageDraw, ImageFont


def read_img(img):
    """
    从输入参数读取图像，转换成二进制字节流格式
    :param img: 存在4种可能形式：图像文件路径名 | 图像文件二进制字节流 | 图像文件二进制字节流的base64编码字符串 | 图像文件二进制字节流的base64编码URL字符串
    :return: 二进制字节流
    """
    try:
        if isinstance(img, bytes):
            return img

        if not isinstance(img, str):
            return None

        if img.endswith('.jpg') or img.endswith('.jpeg') or img.endswith('.png') or img.endswith('.gif') or img.endswith('.bmp'):
            with open(img, 'rb') as file:
                return file.read()

        if img.startswith('data:image/'):
            img = re.sub('^data:image/.+;base64,', '', img)
        img = base64.b64decode(img.encode())
        return img
    except:
        return None


def bin2pil(img):
    img = Image.open(io.BytesIO(img))

    # 自动按拍摄时相机的重心旋转图像
    try:
        for orientation in ExifTags.TAGS.keys():
            if ExifTags.TAGS[orientation] == 'Orientation':
                break
        exif = dict(img._getexif().items())
        if exif[orientation] == 3:
            img = img.rotate(180, expand=True)
        elif exif[orientation] == 6:
            img = img.rotate(270, expand=True)
        elif exif[orientation] == 8:
            img = img.rotate(90, expand=True)
    except:
        pass

    if not img.mode == 'RGB':
        img = img.convert('RGB')

    return img


def pil2np(img):
    return np.asarray(img)


def np2pil(img):
    return Image.fromarray(np.uint8(img))


def pil2url(img):
    output_buffer = io.BytesIO()
    img.save(output_buffer, format='JPEG')
    return 'data:image/jpeg;base64,' + str(base64.b64encode(output_buffer.getvalue()), encoding='utf-8')


def bin2base64(img):
    return str(base64.b64encode(img), encoding='utf-8')


def bin2url(img):
    return pil2url(Image.open(io.BytesIO(img)))


def url2pil(url):
    img_base64 = re.sub('^data:image/.+;base64,', '', url)
    return Image.open(io.BytesIO(base64.b64decode(img_base64.encode())))


def np2url(img):
    return pil2url(Image.fromarray(np.uint8(img)))


def resize_pil(img, new_size=1024):
    img_w, img_h = img.size
    if img_w > new_size:
        ratio = new_size / img_w
        img = img.resize((int(ratio * img_w), int(ratio * img_h)), Image.BICUBIC)
    elif img_h > new_size:
        ratio = new_size / img_h
        img = img.resize((int(ratio * img_w), int(ratio * img_h)), Image.BICUBIC)
    return img


def draw_all_box_and_label_pil(img, boxes, outline='red', width=2, text_color='white', text_bg_color='red', text_size=24, font_path='app/fonts/wqy-zenhei.ttc'):
    draw = ImageDraw.Draw(img)
    for (label, box) in boxes:
        x, y, w, h =box
        draw.rectangle((x, y, x + w, y + h), outline=outline, width=width)

    draw = ImageDraw.Draw(img)  # 图片上打印
    font = ImageFont.truetype(font_path, text_size)

    for (label, box) in boxes:
        x1 = max(box[0], 0)
        y1 = max(box[1] - text_size - 3, 0)
        point = (x1, y1)
        draw.rectangle((x1, y1, x1 + text_size * len(label) / 2 + 24, y1 + text_size), fill=text_bg_color)
        draw.text(point, label, text_color, font=font)  # 参数1：打印坐标，参数2：文本，参数3：字体颜色，参数4：字体

    return img
