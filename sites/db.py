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
        CREATE TABLE IF NOT EXISTS site (
            id INT(11) NOT NULL AUTO_INCREMENT,
            domain VARCHAR(255) NOT NULL,
            data VARCHAR(2048) NOT NULL,
            PRIMARY KEY (id)
        )
    """)
    
    cursor.close()
    connection.close()

def get_site(domain):
    connection = mysql.connector.connect(**dbargs)
    cursor = connection.cursor()
    cursor.execute("""
        SELECT * FROM site WHERE domain = %s
    """, (domain,))
    site = cursor.fetchall()
    cursor.close()
    connection.close()
    return site
