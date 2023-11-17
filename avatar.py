import os
import dotenv
import db
import random
import json


IMAGE_LOCATION = os.getenv('IMAGE_LOCATION')
if IMAGE_LOCATION == None:
    IMAGE_LOCATION = "/data"

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
MAIN_DOMAIN = os.getenv('MAIN_DOMAIN')
if MAIN_DOMAIN == None:
    MAIN_DOMAIN = "shakecities.com"

if MAIN_DOMAIN == "127.0.0.1:5000":
    MAIN_DOMAIN = f"http://{MAIN_DOMAIN}"
else:
    MAIN_DOMAIN = f"https://{MAIN_DOMAIN}"


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def save_avatar(file,owner):
    filename = file.filename
    while os.path.exists(f"{IMAGE_LOCATION}/{filename}"):
        filename = f"{random.randint(0,1000000)}-{filename}"
    file.save(f"{IMAGE_LOCATION}/{filename}")
    user_data = db.get_website_data_raw(owner)
    user_data['avatar'] = MAIN_DOMAIN + "/avatar/" + filename
    db.update_website_data_raw(owner,json.dumps(user_data))
    return filename

def clear(owner):
    user_data = db.get_website_data_raw(owner)
    filename = user_data['avatar'].split('/')[-1]
    os.remove(f"{IMAGE_LOCATION}/{filename}")
    user_data['avatar'] = ""
    db.update_website_data_raw(owner,json.dumps(user_data))
