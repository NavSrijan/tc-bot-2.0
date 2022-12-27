from datetime import datetime, timezone
import discord
from dateutil import tz
import pickle as pkl
from PIL import Image
from io import BytesIO
import requests


def load(filename):
    with open(filename, "rb") as f:
        return pkl.load(f)


def save(obj, filename):
    with open(filename, "wb") as f:
        pkl.dump(obj, f)


def utc_to_local(utc_dt):
    return utc_dt.replace(tzinfo=timezone.utc).astimezone(tz=None)


def utc_to_ist(utc_dt):
    from_zone = tz.tzutc()
    to_zone = tz.gettz("Asia/Kolkata")

    utc_dt = utc_dt.replace(tzinfo=from_zone)
    cc = utc_dt.astimezone(to_zone)

    return cc


def download_and_return_image(url, filename="emojiSuggestion.png") -> discord.File:
    im = Image.open(requests.get(url, stream=True).raw).convert('RGBA')
    with BytesIO() as image_binary:
        im.save(image_binary, 'PNG')
        image_binary.seek(0)
        file = discord.File(fp=image_binary, filename=filename)
    return file

class MorseCode():

    def __init__(self):
        self.data = {
            'a': '.-',
            'b': '-...',
            'c': '-.-.',
            'd': '-..',
            'e': '.',
            'f': '..-.',
            'g': '--.',
            'h': '....',
            'i': '..',
            'j': '.---',
            'k': '-.-',
            'l': '.-..',
            'm': '--',
            'n': '-.',
            'o': '---',
            'p': '.--.',
            'q': '--.-',
            'r': '.-.',
            's': '...',
            't': '-',
            'u': '..-',
            'v': '...-',
            'w': '.--',
            'x': '-..-',
            'y': '-.--',
            'z': '--..',
            ' ': '/',
            '0': '-----',
            '1': '.----',
            '2': '..---',
            '3': '...--',
            '4': '....-',
            '5': '.....',
            '6': '-....',
            '7': '--...',
            '8': '---..',
            '9': '----.',
            '.': '.-.-.-',
            ',': '--..--',
            ':': '---...',
            '?': '..--..',
            "'": '.----.',
            '/': '-..-.',
            '(': '-.--.',
            ')': '-.--.-',
            '"': '.-..-.',
            '': ''
        }

    def encrypt(self, text):
        ll = list(text.lower())
        final = ""
        for i in ll:
            try:
                final += self.data[i] + " "
            except:
                final += " "
        return final

    def decrypt(self, text):
        ll = text.lower().split("/")
        for i, j in enumerate(ll):
            ll[i] = j.split(" ")
        final = ""
        data = dict((v,k) for k,v in self.data.items())
        for i in ll:
            word = ""
            for j in i:
                try:
                    word+= data[j]
                except:
                    word+= " "
            final+=word+" "
        return final