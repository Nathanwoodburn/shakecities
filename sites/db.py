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