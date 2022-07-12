from datetime import datetime, timezone
from dateutil import tz
import pickle as pkl
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
