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

alt_domains = os.getenv('ALT_DOMAINS')

if alt_domains == None:
    alt_domains = []
else:
    alt_domains = alt_domains.split(",")

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

    copy_to_alts(domain)
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
    copy_to_alts(domain)
    return r.text
    
def verify_ALIAS(domain):
    if zone == "":
        get_zone()

    data = {
    "action": "getRecords",
    "zone": zone,
    "name": domain+"."+city_domain,
    "type": "A",
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
    copy_to_alts(domain)
    return r.text

def copy_to_alts(domain):
    # Get DNS from domain and copy to each alt
    data = {
    "action": "getRecords",
    "zone": zone,
    "name": domain+"."+city_domain,
    "type": "",
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
        return
    
    records = r['data']
    
    for alt_domain in alt_domains:
        # Get the zone for the alt
        alt_zone = ""
        data = {
        "action": "getZones"
        }
        r = requests.post(url, headers=headers, json=data)
        r = r.json()
        for tmpzone in r['data']:
            if tmpzone['name'] == alt_domain:
                alt_zone = tmpzone['id']
        print(alt_zone)
        if alt_zone == "":
            continue
        # Delete all records from domain.alt
        data = {
        "action": "getRecords",
        "zone": alt_zone,
        "name": domain+"."+alt_domain,
        "type": "",
        "content": ""
        }
        r = requests.post(url, headers=headers, json=data)
        r = r.json()
        if 'data' in r:
            for record in r['data']:
                data = {
                "action": "deleteRecord",
                "zone": alt_zone,
                "record": record['uuid']
                }
                r = requests.post(url, headers=headers, json=data)
                print(r.text)

        # Add each record to each alt
        for record in records:
            data = {
                "action": "addRecord",
                "zone": alt_zone,
                "type": record['type'],
                "name": domain+"."+alt_domain,
                "content": record['content'],
            }
            print(data)
            r = requests.post(url, headers=headers, json=data)
            print(r.text)
        # Add TLSA record if it doesn't exist
        data = {
            "action": "getRecords",
            "zone": alt_zone,
            "name": "_443._tcp."+domain+"."+alt_domain,
            "type": "TLSA",
            "content": ""
        }
        r = requests.post(url, headers=headers, json=data)
        r = r.json()
        if 'data' not in r:
            # Get alt TLSA from _443._tcp.alt_domain
            data = {
                "action": "getRecords",
                "zone": alt_zone,
                "name": "_443._tcp."+alt_domain,
                "type": "TLSA",
                "content": ""
            }
            r = requests.post(url, headers=headers, json=data)
            r = r.json()
            if 'data' not in r:
                continue
            for record in r['data']:
                ALT_TLSA = record['content']

            data = {
                "action": "addRecord",
                "zone": alt_zone,
                "type": "TLSA",
                "name": "_443._tcp."+domain+"."+alt_domain,
                "content": ALT_TLSA,
            }
            r = requests.post(url, headers=headers, json=data)
            print(r.text)
