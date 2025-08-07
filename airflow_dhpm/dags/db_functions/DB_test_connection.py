import pymysql
from dotenv import load_dotenv
import os

# Load variables from .env file
load_dotenv('.env')

def mysql_test_connection():
    host = os.getenv('MYSQL_HOST')
    user = os.getenv('MYSQL_USER')
    password = os.getenv('MYSQL_PASSWORD')

    try:
        connection = pymysql.connect(
            host=host,           # Use 'db' service name if running from another container, 'localhost' if from host and port is mapped
            user=user,
            password=password
        )
        print("Connection to MySQL DB successful")
        return True
    except Exception as e:
        print(f"Error: {e}")
        return False
    finally:
        if 'connection' in locals() and connection.open:
            connection.close()

# Example usage:
if __name__ == "__main__":
    mysql_test_connection()