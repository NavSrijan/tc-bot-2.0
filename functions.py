from datetime import datetime, timezone
import discord
from dateutil import tz
import pickle as pkl
from PIL import Image
from io import BytesIO
import requests
#from database import Database, DATABASE_URL

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

def download_and_return_image(url) -> discord.File:
    im = Image.open(requests.get(url, stream=True).raw).convert('RGBA')
    with BytesIO() as image_binary:
            im.save(image_binary, 'PNG')
            image_binary.seek(0)
            file=discord.File(fp=image_binary, filename='emojiSuggestion.png')
    return file
