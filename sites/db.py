import mysql.connector
import os
import dotenv
import json

dotenv.load_dotenv()

# Database connection
dbargs = {
    'host':os.getenv('DB_HOST'),
    'user':os.getenv('DB_USER'),
    'password':os.getenv('DB_PASSWORD'),
    'database':os.getenv('DB_NAME')
}

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
        return ""
    
    parsed = data[0][2]
    parsed = json.loads(parsed)

    return parsed

def get_website_wallet(domain,token):
    connection = mysql.connector.connect(**dbargs)
    cursor = connection.cursor()
    cursor.execute("""
        SELECT * FROM site WHERE domain = %s
    """, (domain,))
    data = cursor.fetchall()
    cursor.close()
    connection.close()
    
    if data == []:
        return ""
    
    parsed = data[0][2]
    parsed = json.loads(parsed)
    if token in parsed:
        parsed = parsed[token]
        return parsed
    
    return ""