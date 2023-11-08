import mysql.connector
import os
import dotenv

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
            data VARCHAR(2048) NOT NULL,
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
        cursor.execute("""
            INSERT INTO site (domain, data)
            VALUES (%s, %s)
        """, (domain, ""))
        connection.commit()
        cursor.close()
        connection.close()
        return ""
    return data[0][2]

def update_website_data(domain,data):
    connection = mysql.connector.connect(**dbargs)
    cursor = connection.cursor()
    cursor.execute("""
        UPDATE site SET data = %s WHERE domain = %s
    """, (data, domain))
    connection.commit()
    cursor.close()
    connection.close()