import requests
import os
import dotenv

dotenv.load_dotenv()
zone = ""
varo_api = os.getenv('VARO')
city_domain = os.getenv('CITY_DOMAIN')


def update_auth(auth,domain):
    print("TXT: " + auth, "DOMAIN: " + domain, flush=True)

    record = get_auth_id(domain)
    if record == "":
        data = {
        "action": "addRecord",
        "zone": zone,
        "type": "TXT",
        "name": domain,
        "content": auth,
        }
    else:
        data = {
        "action": "updateRecord",
        "zone": zone,
        "record": record,
        "column": "content",
        "value": auth
        }
    if auth == "" and record == "":
        return
    if auth == "" and record != "":
        data = {
        "action": "deleteRecord",
        "zone": zone,
        "record": record
        }
    # Update TXT record
    url = "https://reg.woodburn.au/api"
    headers = {
        'Authorization': 'Bearer '+varo_api,
        'Content-Type': 'application/json'
    }
    r = requests.put(url, headers=headers, json=data)
    return r.text


def get_auth_id(domain):
    if zone == "":
        get_zone()

    data = {
    "action": "getRecords",
    "zone": zone,
    "name": "",
    "type": "TXT",
    "content": ""
    }
    url = "https://reg.woodburn.au/api"
    headers = {
        'Authorization': 'Bearer '+varo_api,
        'Content-Type': 'application/json'
    }
    r = requests.post(url, headers=headers, json=data)
    r = r.json()
    for record in r['data']:
        if record['name'] == domain + "." + city_domain:
            if 'profile avatar=' not in record['content']:
                return record['uuid']
    return ""

def get_auth(domain):
    if zone == "":
        get_zone()

    data = {
    "action": "getRecords",
    "zone": zone,
    "name": "",
    "type": "TXT",
    "content": ""
    }
    url = "https://reg.woodburn.au/api"
    headers = {
        'Authorization': 'Bearer '+varo_api,
        'Content-Type': 'application/json'
    }
    r = requests.post(url, headers=headers, json=data)
    r = r.json()
    for record in r['data']:
        if record['name'] == domain + "." + city_domain:
            if 'profile avatar=' not in record['content']:
                return record['content']
    return ""

def get_zone():
    global zone
    url = "https://reg.woodburn.au/api"
    headers = {
        'Authorization': 'Bearer '+varo_api,
        'Content-Type': 'application/json'
    }
    data = {
        "action": "getZones"
    }
    r = requests.post(url, headers=headers, json=data)
    r = r.json()
    for domain in r['data']:
        if domain['name'] == city_domain:
            zone = domain['id']
            return domain['id']
        
def update_avatar(avatar,domain):
    if zone == "":
        get_zone()

    data = {
    "action": "getRecords",
    "zone": zone,
    "name": "",
    "type": "TXT",
    "content": ""
    }
    url = "https://reg.woodburn.au/api"
    headers = {
        'Authorization': 'Bearer '+varo_api,
        'Content-Type': 'application/json'
    }
    r = requests.post(url, headers=headers, json=data)
    r = r.json()
    record_id = ""
    for record in r['data']:
        if record['name'] == domain + "." + city_domain:
            if 'profile avatar=' in record['content']:
                if record['content'].split("profile avatar=")[1] == avatar:
                    print("Avatar already set", flush=True)
                    return "Avatar already set"
                record_id = record['uuid']

    if record_id == "":
        data = {
        "action": "addRecord",
        "zone": zone,
        "type": "TXT",
        "name": domain,
        "content": "profile avatar=" + avatar,
        }
    else:
        data = {
        "action": "updateRecord",
        "zone": zone,
        "record": record,
        "column": "content",
        "value": "profile avatar=" + avatar
        }
    if avatar == "" and record_id == "":
        return
    if avatar == "" and record_id != "":
        data = {
        "action": "deleteRecord",
        "zone": zone,
        "record": record_id
        }

    r = requests.post(url, headers=headers, json=data)
    return r.text
    