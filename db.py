import mysql.connector
from mysql.connector import Error
from werkzeug.security import generate_password_hash, check_password_hash

connection = None

def init_app(app):
    global connection
    try:
        connection = mysql.connector.connect(
            host="localhost",
            user="mlcat",
            password="password",
            database="smart_health"
        )
        if connection.is_connected():
            print("Connected to MySQL database")
    except Error as e:
        print(f"Error connecting to MySQL: {e}")

def create_user(username, password):
    try:
        cursor = connection.cursor()
        hashed_password = generate_password_hash(password)
        query = "INSERT INTO users (username, password) VALUES (%s, %s)"
        cursor.execute(query, (username, hashed_password))
        connection.commit()
        cursor.close()  # Ensure the cursor is closed after use
        return True
    except mysql.connector.IntegrityError:
        print("Username already exists.")
        return False
    except Exception as e:
        print(f"Error creating user: {e}")
        return False

def verify_user(username, password):
    try:
        cursor = connection.cursor()
        query = "SELECT password FROM users WHERE username = %s"
        cursor.execute(query, (username,))
        result = cursor.fetchone()
        cursor.close()  # Ensure the cursor is closed after use
        if result and check_password_hash(result[0], password):
            return True
        return False
    except Exception as e:
        print(f"Error verifying user: {e}")
        return False

# Consider adding a function to close the connection when app shuts down
def close_connection():
    if connection and connection.is_connected():
        connection.close()
        print("MySQL connection closed.")

'''
CREATE DATABASE smart_health;

USE smart_health;

CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(100) NOT NULL UNIQUE,
    password VARCHAR(100) NOT NULL
);

'''


'''
-- Log in to MySQL as root or an admin user
CREATE USER 'mlcat'@'localhost' IDENTIFIED BY 'password';

-- Grant all privileges on your database (e.g. smart_health)
GRANT ALL PRIVILEGES ON smart_health.* TO 'mlcat'@'localhost';

-- Apply the changes
FLUSH PRIVILEGES;

'''