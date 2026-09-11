import mysql.connector
import os
import dotenv
import json
import random
import re
from bs4 import BeautifulSoup

dotenv.load_dotenv()

# Database connection
dbargs = {
    'host':os.getenv('DB_HOST'),
    'user':os.getenv('DB_USER'),
    'password':os.getenv('DB_PASSWORD'),
    'database':os.getenv('DB_NAME')
}

def check_tables():
    connection = mysql.connector.connect(**dbargs)
    cursor = connection.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INT(11) NOT NULL AUTO_INCREMENT,
            email VARCHAR(255) NOT NULL,
            domain VARCHAR(255) NOT NULL,
            password VARCHAR(255) NOT NULL,
            token VARCHAR(255) NOT NULL,
            PRIMARY KEY (id)
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS site (
            id INT(11) NOT NULL AUTO_INCREMENT,
            domain VARCHAR(255) NOT NULL,
            data JSON,
            PRIMARY KEY (id)
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS tribes (
            id INT(11) NOT NULL AUTO_INCREMENT,
            tribe VARCHAR(255) NOT NULL,
            data JSON,
            owner VARCHAR(255) NOT NULL,
            PRIMARY KEY (id)
        )
    """)
    cursor.close()
    connection.close()
    print("Checked tables")

def add_user(email,domain,password,token):
    connection = mysql.connector.connect(**dbargs)
    cursor = connection.cursor()

    cursor.execute("""
        INSERT INTO users (email, domain, password, token)
        VALUES (%s, %s, %s, %s)
    """, (email, domain, password, token))
    connection.commit()
    cursor.close()
    connection.close()

def search_users(email):
    connection = mysql.connector.connect(**dbargs)
    cursor = connection.cursor()
    cursor.execute("""
        SELECT * FROM users WHERE email = %s
    """, (email,))
    users = cursor.fetchall()
    cursor.close()
    connection.close()
    return users

def search_users_domain(domain):
    connection = mysql.connector.connect(**dbargs)
    cursor = connection.cursor()
    cursor.execute("""
        SELECT * FROM users WHERE domain = %s
    """, (domain,))
    users = cursor.fetchall()
    cursor.close()
    connection.close()
    return users

def search_users_token(token):
    connection = mysql.connector.connect(**dbargs)
    cursor = connection.cursor()
    query = "SELECT * FROM users WHERE token LIKE %s"
    cursor.execute(query, ('%' + token + '%',))

    users = cursor.fetchall()
    cursor.close()
    connection.close()
    return users

def update_tokens(id,tokens):
    tokens = ','.join(tokens)
    connection = mysql.connector.connect(**dbargs)
    cursor = connection.cursor()
    cursor.execute("""
        UPDATE users SET token = %s WHERE id = %s
    """, (tokens, id))
    connection.commit()
    cursor.close()
    connection.close()

def update_password(id, password):
    connection = mysql.connector.connect(**dbargs)
    cursor = connection.cursor()
    cursor.execute("""
        UPDATE users SET password = %s WHERE id = %s
    """, (password, id))
    connection.commit()
    cursor.close()
    connection.close()

def get_website_data(domain):
    connection = mysql.connector.connect(**dbargs)
    cursor = connection.cursor()
    cursor.execute("""
        SELECT * FROM site WHERE domain = %s
    """, (domain,))
    data = cursor.fetchall()
    cursor.close()
    connection.close()
    
    if data == []:
        # Create new entry
        connection = mysql.connector.connect(**dbargs)
        cursor = connection.cursor()
        data = {
            "data": ""
        }
        insert_query = "INSERT INTO site (data,domain) VALUES (%s,%s)"
        cursor.execute(insert_query, (json.dumps(data), domain))
        connection.commit()
        cursor.close()
        connection.close()
        return ""
    
    parsed = data[0][2]
    parsed = json.loads(parsed)
    parsed = parsed['data']
    # Decoding
    parsed = parsed.encode('utf-8').decode('unicode-escape')

    return parsed

def get_website_data_raw(domain):
    connection = mysql.connector.connect(**dbargs)
    cursor = connection.cursor()
    cursor.execute("""
        SELECT * FROM site WHERE domain = %s
    """, (domain,))
    data = cursor.fetchall()
    cursor.close()
    connection.close()
    
    if data == []:
        # Create new entry
        connection = mysql.connector.connect(**dbargs)
        cursor = connection.cursor()
        data = {
            "data": ""
        }
        insert_query = "INSERT INTO site (data,domain) VALUES (%s,%s)"
        cursor.execute(insert_query, (json.dumps(data), domain))
        connection.commit()
        cursor.close()
        connection.close()
        return ""
    
    parsed = data[0][2]
    parsed = json.loads(parsed)

    return parsed

def update_website_data(domain,data):
    data = get_website_data_raw(domain)

    connection = mysql.connector.connect(**dbargs)
    cursor = connection.cursor()
    # Update json object
    data['data'] = data

    update_query = "UPDATE site SET data = %s WHERE domain = %s"
    cursor.execute(update_query, (json.dumps(data), domain))
    
    connection.commit()
    cursor.close()
    connection.close()

def update_website_data_raw(domain,data):
    connection = mysql.connector.connect(**dbargs)
    cursor = connection.cursor()
    # Update json object
    data = json.loads(data)

    update_query = "UPDATE site SET data = %s WHERE domain = %s"
    cursor.execute(update_query, (json.dumps(data), domain))
    
    connection.commit()
    cursor.close()
    connection.close()

def update_website_wallet(domain,token,address):
    data = get_website_data_raw(domain)

    connection = mysql.connector.connect(**dbargs)
    cursor = connection.cursor()
    # Update json object
    data[token] = address

    update_query = "UPDATE site SET data = %s WHERE domain = %s"
    cursor.execute(update_query, (json.dumps(data), domain))
    
    connection.commit()
    cursor.close()
    connection.close()

def site_has_content(site_data):
    if not site_data:
        return False
    try:
        if isinstance(site_data, (bytes, bytearray)):
            site_data = site_data.decode('utf-8')
        if isinstance(site_data, str):
            parsed = json.loads(site_data)
        elif isinstance(site_data, dict):
            parsed = site_data
        else:
            return False

        if not isinstance(parsed, dict):
            return False

        html = parsed.get('data', '')
        if not html or not isinstance(html, str):
            return False

        html = html.strip()
        if not html:
            return False

        try:
            html = html.encode('utf-8').decode('unicode-escape')
        except Exception:
            pass

        try:
            soup = BeautifulSoup(html, 'html.parser')
            text = soup.get_text(strip=True).replace('\xa0', '').replace('&nbsp;', '')
            has_media = bool(soup.find(['img', 'iframe', 'video', 'audio', 'svg', 'canvas', 'object', 'embed', 'table', 'hr']))
            return bool(text or has_media)
        except Exception:
            clean = re.sub(r'<[^>]*>', '', html).replace('&nbsp;', '').strip()
            return bool(clean)
    except Exception:
        return False

def get_random_sites():
    connection = mysql.connector.connect(**dbargs)
    cursor = connection.cursor()
    cursor.execute("""
        SELECT * FROM site
    """)
    data = cursor.fetchall()
    cursor.close()
    connection.close()

    sites_with_content = []
    for site in data:
        if site_has_content(site[2]):
            sites_with_content.append(site[1])

    # Randomly pick up to 5
    count = min(len(sites_with_content), 5)
    if count > 0:
        return random.sample(sites_with_content, count)

    return []

def get_tribes():
    connection = mysql.connector.connect(**dbargs)
    cursor = connection.cursor()
    cursor.execute("""
        SELECT * FROM tribes
    """)
    data = cursor.fetchall()
    cursor.close()
    connection.close()

    tribes = []
    for tribe in data:
        tribes.append(tribe[1])

    return tribes

def get_user_tribes(user):
    connection = mysql.connector.connect(**dbargs)
    cursor = connection.cursor()
    cursor.execute("""
        SELECT * FROM tribes WHERE owner = %s
    """, (user,))
    data = cursor.fetchall()
    cursor.close()
    connection.close()

    # Also check members
    connection = mysql.connector.connect(**dbargs)
    cursor = connection.cursor()
    cursor.execute("""
        SELECT * FROM tribes
    """)
    data2 = cursor.fetchall()
    cursor.close()
    connection.close()


    for tribe in data2:
        tribe = json.loads(tribe[2])
        if user in tribe['members']:
            data.append(tribe)


    return len(data)

def get_user_owned_tribe(user):
    connection = mysql.connector.connect(**dbargs)
    cursor = connection.cursor()
    cursor.execute("""
        SELECT * FROM tribes WHERE owner = %s
    """, (user,))
    data = cursor.fetchall()
    cursor.close()
    connection.close()

    return data

def create_tribe(tribe,owner):
    # Get users' tribes
    if (get_user_tribes(owner) > 0):
        return False


    connection = mysql.connector.connect(**dbargs)
    cursor = connection.cursor()
    data = {
        "data": "",
        "members": [
            owner
        ]
    }
    insert_query = "INSERT INTO tribes (data,tribe,owner) VALUES (%s,%s,%s)"
    cursor.execute(insert_query, (json.dumps(data), tribe, owner))
    connection.commit()
    cursor.close()
    connection.close()
    return True

def get_tribe_data_raw(tribe):
    connection = mysql.connector.connect(**dbargs)
    cursor = connection.cursor()
    cursor.execute("""
        SELECT * FROM tribes WHERE tribe = %s
    """, (tribe,))
    data = cursor.fetchall()
    cursor.close()
    connection.close()

    if len(data) == 0:
        return False

    return json.loads(data[0][2])

def check_tribe_owner(tribe,owner):
    connection = mysql.connector.connect(**dbargs)
    cursor = connection.cursor()
    cursor.execute("""
        SELECT * FROM tribes WHERE tribe = %s
    """, (tribe,))
    data = cursor.fetchall()
    cursor.close()
    connection.close()

    if len(data) == 0:
        return False

    if data[0][3] == owner:
        return True
    else:
        return False
    
def update_tribe_data_raw(tribe,data):
    connection = mysql.connector.connect(**dbargs)
    cursor = connection.cursor()
    # Update json object
    data = json.loads(data)

    update_query = "UPDATE tribes SET data = %s WHERE tribe = %s"
    cursor.execute(update_query, (json.dumps(data), tribe))
    
    connection.commit()
    cursor.close()
    connection.close()

def delete_tribe(tribe):
    connection = mysql.connector.connect(**dbargs)
    cursor = connection.cursor()
    cursor.execute("""
        DELETE FROM tribes WHERE tribe = %s
    """, (tribe,))
    connection.commit()
    cursor.close()
    connection.close()

def rename_tribe(old,new):
    connection = mysql.connector.connect(**dbargs)
    cursor = connection.cursor()
    cursor.execute("""
        UPDATE tribes SET tribe = %s WHERE tribe = %s
    """, (new,old))
    connection.commit()
    cursor.close()
    connection.close()