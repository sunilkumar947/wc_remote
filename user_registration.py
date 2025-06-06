import bcrypt
import mysql.connector

class UserRegistration:
    def __init__(self, db_config):
        self.connection = mysql.connector.connect(**db_config)
        self.cursor = self.connection.cursor()

    def hash_password(self, password):
        # Hash the password with bcrypt
        salt = bcrypt.gensalt()
        return bcrypt.hashpw(password.encode(), salt)

    def register_user(self, username, password):
        try:
            user_password = self.hash_password(password)
            sql = "INSERT INTO users (username, password) VALUES (%s, %s)"
            self.cursor.execute(sql, (username, user_password.decode()))
            self.connection.commit()
            print("User registered successfully!")
        except mysql.connector.IntegrityError:
            print("Username already exists.")
        except Exception as e:
            print(f"An error occurred: {e}")
        finally:
            self.cursor.close()
            self.connection.close()

