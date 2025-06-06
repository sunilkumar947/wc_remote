from datetime import datetime,timedelta
import mysql.connector
from mysql.connector import Error
import bcrypt

class DatabaseHandler:
    def __init__(self,host,user,password,database):
    
        try:
            # Establish a connection to the MySQL database
            print("in databasehandler")
            self.connection = mysql.connector.connect(
                host=host,
                user=user,
                password=password,
                database=database
            )
         
            self.cursor = self.connection.cursor()
            print("Database connected successfully!")
        except Error as e:
            print(f"Error: {e}")
            self.connection = None
  
    
    
    def insert_data(self, table, data):
        """Insert data into a specific table."""
        if not self.connection:
            print("Database connection not established.")
            return
        try:
            print(f"Inserting into table {table} with data: {data}")
            placeholders = ", ".join(["%s"] * len(data))
            query = f"INSERT INTO {table} VALUES (NULL, {placeholders})"
            self.cursor.execute(query, data)
            self.connection.commit()
            print(f"Data inserted into {table} successfully.")
        except Error as e:
            print(f"Error inserting data: {e}")
    
    def fetch_all_users(self):
        """Fetch all users from the database."""
        if not self.connection:
            print("Database connection not established.")
            return []
        try:
            self.connection.commit()  
            cursor = self.connection.cursor()
            cursor.execute("SELECT username, user_id FROM users")  
            users = cursor.fetchall()  
            
            print(users, 'Updated Users List')
            return users 
        except Exception as e:
            print("Error fetching users:", e)
            return []

    # def fetch_all_users(self):
    #     """Fetch all users from the database."""
    #     try:
    #         cursor = self.connection.cursor()
    #         cursor.execute("SELECT username, user_id FROM users")  
    #         users = cursor.fetchall()  
    #         print(users,'uuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuu')
    #         return users 
    #     except Exception as e:
    #         print("Error fetching users:", e)
    #         return []
        
        
    def fetch_user_details(self, uuid):
        if not self.connection:
            print("Database connection not established.")
            return None

        try:
            query = "SELECT username, email , user_id, status FROM users WHERE user_id = %s"
            self.cursor.execute(query, (uuid,))
            result = self.cursor.fetchone()
            if result:
                return {"username": result[0], "email": result[1], "user_id": result[2], "status": result[3]}
            return None
        except Error as e:
            print(f"Error fetching user details: {e}")
            return None      

    def fetch_login_details(self, uuid, start_date=None, end_date=None):
        if not self.connection:
            print("Database connection not established.")
            return None

        try:
            if start_date and end_date:
                query = """
                    SELECT date, login_time, break_time, screen_time, logout_time
                    FROM work_time
                    WHERE user_id = %s AND date BETWEEN %s AND %s
                """
                self.cursor.execute(query, (uuid, start_date, end_date))
            else:
                query = """
                    SELECT date, login_time, break_time, screen_time, logout_time
                    FROM work_time
                    WHERE user_id = %s
                """
                self.cursor.execute(query, (uuid,))
            
            result = self.cursor.fetchall()
            return result if result else None

        except Error as e:
            print(f"Error fetching login details: {e}")
            return None

        
    def fetch_activity_details(self, uuid, start_date=None, end_date=None):
        if not self.connection:
            print("Database connection not established.")
            return None

        try:
            if start_date and end_date:
                query = """
                    SELECT date, app_name, url, duration
                    FROM app_usage
                    WHERE user_id = %s AND date BETWEEN %s AND %s
                """
                self.cursor.execute(query, (uuid, start_date, end_date))
            else:
                query = """
                    SELECT date, app_name, url, duration
                    FROM app_usage
                    WHERE user_id = %s
                """
                self.cursor.execute(query, (uuid,))
            
            result = self.cursor.fetchall()
            print(result, 'Fetched Activity Data')
            return result if result else None 
        except Error as e:
            print(f"Error fetching activity details: {e}")
            return None


    def fetch_screenshots(self, user_id, start_date, end_date):
        query = """
            SELECT timestamp, screenshot_path 
            FROM screenshots 
            WHERE user_id = %s 
            AND DATE(timestamp) BETWEEN %s AND %s
            ORDER BY timestamp ASC
        """
        self.cursor.execute(query, (user_id, start_date, end_date))
        return self.cursor.fetchall()       
        
    def update_user_status(self, uuid, status):
        if not self.connection:
            print("Database connection not established.")
            return False

        try:
            query = "UPDATE users SET status = %s WHERE user_id = %s"
            self.cursor.execute(query, (status, uuid))
            self.connection.commit()
            return True
        except Exception as e:
            print(f"Error updating user status: {e}")
            return False
    
    def get_user_by_email(self, email):
        self.cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
        return self.cursor.fetchone()

    def get_username_by_email(self, email):
        """Retrieve the username using the email address."""
        self.cursor = self.connection.cursor(dictionary=True)
        self.cursor.execute("SELECT username FROM users WHERE email = %s", (email,))
        result = self.cursor.fetchone()
        if result:
            return result["username"] 
        return None

    def update_password(self, email, new_password):
        hashed_password = bcrypt.hashpw(new_password.encode(), bcrypt.gensalt()).decode()
        self.cursor.execute("UPDATE users SET user_password = %s WHERE email = %s", (hashed_password, email))
        self.connection.commit()
        
    
    def close(self):
        """Close the database connection."""
        if self.connection:
            self.cursor.close()
            self.connection.close()
            print("Database connection closed.")

    # def query_data(self, query, params=None):
    #     """Fetch data from the database."""
    #     if not self.connection:
    #         print("Database connection not established.")
    #         return None
    #     try:
    #         self.cursor.execute(query, params)
    #         result = self.cursor.fetchall()
    #         return result
    #     except Error as e:
    #         print(f"Error querying data: {e}")
    #         return None
        
        
    # def verify_user(self, username, password):
    #     """Verify user credentials against the database."""
    #     cursor = self.connection.cursor(dictionary=True)
    #     cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
    #     user = cursor.fetchone()

    #     if user:
    #         # Compare the hashed password in the database with the entered password
    #         if bcrypt.checkpw(password.encode('utf-8'), user['password'].encode('utf-8')):
    #             return True
    #     return False    


            
            
            
# if __name__ == "__main__":
#     db_handler = DatabaseHandler()

 
#     if db_handler.connection:
#         print("Connection to the database was successful.")
#     else:
#         print("Failed to connect to the database.")


#     try:
#         db_handler.query_data("SELECT DATABASE();")  # Check current database
#         print("Database is operational.")
#     except Exception as e:
#         print(f"Error during query execution: {e}")
    

#     db_handler.close()            
