from PyQt6.QtWidgets import QDialog, QVBoxLayout,QApplication, QLineEdit, QPushButton, QMessageBox
from registration import RegistrationWindow
from authenticate_user import UserAuthentication
from admin_login import AdminLoginWindow
from forget_credentials import ForgotCredentialsWindow
import sys
from main_window import MainWindow 

class LoginWindow(QDialog):
    def __init__(self,db_handler):
        
        DEFAULT_ADMIN_CREDENTIALS = {
        "username": "admin",
        "password": "admin123"
    }
        super().__init__()
        self.setWindowTitle("Login")
        self.setFixedSize(400, 200)
        self.db_handler = db_handler
        self.user_id = None
        self.authenticator = UserAuthentication(db_handler)
        
        # Create layout
        layout = QVBoxLayout()
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Username")
        layout.addWidget(self.username_input)

        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Password")
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        layout.addWidget(self.password_input)

        self.login_button = QPushButton("Login")
        self.login_button.clicked.connect(self.authenticate_user)
        layout.addWidget(self.login_button)
        
        self.admin_login_button = QPushButton("Login as Admin")
        self.admin_login_button.clicked.connect(self.open_admin_login)
        layout.addWidget(self.admin_login_button)

        self.register_button = QPushButton("Register")
        self.register_button.clicked.connect(self.open_registration)
        layout.addWidget(self.register_button)
        
        self.forgot_button = QPushButton("Forgot Username/Password?")
        self.forgot_button.clicked.connect(self.forgot_credentials)
        layout.addWidget(self.forgot_button)
        
        
        self.setLayout(layout)
      
        
    def authenticate_user(self):
        username = self.username_input.text()
        password = self.password_input.text()

        user_record = self.authenticator.authenticate_user(username, password)
        print(user_record,'ssssssssssssssssssssssssssssssssssssss')
        if not user_record:  
            QMessageBox.warning(self, "Login Failed", "Invalid username or password.")
            return  

        # Ensure status is treated as an integer (0 = inactive, 1 = active)
        status = (user_record.get("status"))  
        print(status,'aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa')
        if status == 'Inactive':  # User is inactive
            QMessageBox.warning(self, "Access Denied", "Your account is inactive. Contact admin.")
            return  

        self.user_id = user_record.get("user_id")
        self.username = user_record.get("username")  # Store the username
        print(f"Logged in as: {self.username} (User ID: {self.user_id})")
        QMessageBox.information(self, "Login Successful", f"Welcome, {username}!")
        self.accept() 

    
    def open_admin_login(self):
        """Open admin login panel."""
        admin_login = AdminLoginWindow()
        if admin_login.exec():
            QMessageBox.information(self, "Admin Login", "Welcome, Admin!")
            self.accept()
    
    
    def open_registration(self):
        self.registration_window = RegistrationWindow(self.db_handler)
        self.registration_window.exec()
        
    def forgot_credentials(self):
        """Open Forgot Password window."""
        self.forgot_password_window = ForgotCredentialsWindow(self.db_handler)
        self.forgot_password_window.exec()
     
    
    def closeEvent(self, event):
        """Override the close event to properly exit the application."""
        event.accept()  
        self.exit_application()  

    def exit_application(self):
        """Exit the application completely."""
        QApplication.quit()  # Properly shut down the application
        sys.exit(0)  
        
                  
    # def authenticate_user(self):
    #     username = self.username_input.text()
    #     password = self.password_input.text()

    #     # Replace with actual authentication logic
    #     if self.authenticator.authenticate_user(username, password):
    #         QMessageBox.information(self, "Login Successful", "Welcome!")
    #         self.accept()  # Close dialog with success
    #     else:
    #         QMessageBox.warning(self, "Login Failed", "Invalid username or password.")

    


















# from PyQt6.QtWidgets import QDialog, QVBoxLayout, QLineEdit, QPushButton, QMessageBox
# from registration import RegistrationWindow
# from database import DatabaseHandler
# from authenticate_user import UserAuthentication
# from main_window import MainWindow 

# class LoginWindow(QDialog):
#     print("inlogin")
#     def __init__(self,db_handler,on_success_callback):
#         super().__init__()
#         self.setWindowTitle("Login")
#         self.setFixedSize(400, 200)
#         self.db_handler = db_handler
#         self.authenticator = UserAuthentication(db_handler)
#         self.on_success_callback = on_success_callback
        
#         layout = QVBoxLayout()
#         self.username_input = QLineEdit()
#         self.username_input.setPlaceholderText("Username")
#         layout.addWidget(self.username_input)

#         self.password_input = QLineEdit()
#         self.password_input.setPlaceholderText("Password")
#         self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
#         layout.addWidget(self.password_input)

#         self.login_button = QPushButton("Login")
#         self.login_button.clicked.connect(self.authenticate_user)
#         layout.addWidget(self.login_button)
        
        # self.register_button = QPushButton("Register")
        # self.register_button.clicked.connect(self.open_registration)
        # layout.addWidget(self.register_button)
        # self.setLayout(layout)
        

#     def authenticate_user(self):
#             print("Authenticating user...")
#             username = self.username_input.text()
#             password = self.password_input.text()

#             if self.authenticator.authenticate_user(username, password):
#                 QMessageBox.information(self, "Login Successful", "Welcome!")
#                 self.on_success_callback()
#                 self.accept()
#             else:
#                 QMessageBox.warning(self, "Login Failed", "Invalid username or password.")


   
        
    # def open_registration(self):
    #     self.registration_window = RegistrationWindow(self.db_handler)
    #     self.registration_window.exec()