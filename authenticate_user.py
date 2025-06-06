import bcrypt
import mysql.connector


class UserAuthentication:
    def __init__(self, db_handler): 
        self.connection = db_handler.connection  
        self.cursor = self.connection.cursor()

    def verify_password(self, entered_password, stored_password_hash):
        # Compare the entered password with the stored hash
        return bcrypt.checkpw(entered_password.encode(), stored_password_hash.encode())

    def authenticate_user(self, username, password):
        try:
            sql = "SELECT user_id,username,user_password,status  FROM users WHERE username = %s"
            self.cursor.execute(sql, (username,))
            result = self.cursor.fetchone()
            if result  and len(result) == 4:
                user_id,username,stored_password_hash,status = result
                if self.verify_password(password, stored_password_hash):
                    print("Login successful!")
                    return {"user_id": user_id ,'username':username, "status": status}
                else:
                    print("Invalid password.")
            else:
                print("User not found.")
        except Exception as e:
            print(f"An error occurred: {e}")
        
        return False

