import requests
import os
import dotenv

dotenv.load_dotenv()
zone = ""
TLSA = ""
REG_KEY = os.getenv('REG_KEY')
city_domain = os.getenv('CITY_DOMAIN')
if city_domain == "localhost":
    city_domain = "exampledomainnathan1"

server_ip = os.getenv('CITY_IP')

def update_auth(auth,domain):
    verify_ALIAS(domain)
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
        'Authorization': 'Bearer '+REG_KEY,
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
    "name": domain + "." + city_domain,
    "type": "TXT",
    "content": ""
    }
    url = "https://reg.woodburn.au/api"
    headers = {
        'Authorization': 'Bearer '+REG_KEY,
        'Content-Type': 'application/json'
    }
    r = requests.post(url, headers=headers, json=data)
    r = r.json()
    if 'data' not in r:
        return ""
    for record in r['data']:
        if 'profile avatar=' not in record['content']:
            return record['uuid']
    return ""

def get_auth(domain):
    if zone == "":
        get_zone()

    data = {
    "action": "getRecords",
    "zone": zone,
    "name": domain + "." + city_domain,
    "type": "TXT",
    "content": ""
    }
    url = "https://reg.woodburn.au/api"
    headers = {
        'Authorization': 'Bearer '+REG_KEY,
        'Content-Type': 'application/json'
    }
    r = requests.post(url, headers=headers, json=data)
    r = r.json()
    if 'data' not in r:
        return ""

    for record in r['data']:
        if 'profile avatar=' not in record['content']:
            return record['content']
    return ""

def get_zone():
    global zone
    global TLSA
    url = "https://reg.woodburn.au/api"
    headers = {
        'Authorization': 'Bearer '+REG_KEY,
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
    
    data = {
        "action": "getRecords",
        "zone": zone,
        "name": "*."+city_domain,
        "type": "TLSA",
        "content": ""
    }
    r = requests.post(url, headers=headers, json=data)
    r = r.json()
    for record in r['data']:
        TLSA = record['content']
    return zone

        
def update_avatar(avatar,domain):
    verify_ALIAS(domain)
    if zone == "":
        get_zone()

    data = {
    "action": "getRecords",
    "zone": zone,
    "name": domain + "." + city_domain,
    "type": "TXT",
    "content": ""
    }
    url = "https://reg.woodburn.au/api"
    headers = {
        'Authorization': 'Bearer '+REG_KEY,
        'Content-Type': 'application/json'
    }
    r = requests.post(url, headers=headers, json=data)
    r = r.json()
    record_id = ""
    if 'data' in r:
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
        "record": record_id,
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
    
def verify_ALIAS(domain):
    if zone == "":
        get_zone()

    data = {
    "action": "getRecords",
    "zone": zone,
    "name": domain+"."+city_domain,
    "type": "ALIAS",
    "content": ""
    }
    url = "https://reg.woodburn.au/api"
    headers = {
        'Authorization': 'Bearer '+REG_KEY,
        'Content-Type': 'application/json'
    }
    r = requests.post(url, headers=headers, json=data)
    r = r.json()
    if 'data' in r:
        return

    data = {
        "action": "addRecord",
        "zone": zone,
        "type": "A",
        "name": domain,
        "content": server_ip,
        }
    r = requests.post(url, headers=headers, json=data)
    data = {
        "action": "addRecord",
        "zone": zone,
        "type": "TLSA",
        "name": "_443._tcp."+domain+"."+city_domain,
        "content": TLSA,
        }
    r = requests.post(url, headers=headers, json=data)
    return r.text