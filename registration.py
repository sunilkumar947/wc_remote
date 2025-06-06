from PyQt6.QtWidgets import QDialog, QVBoxLayout, QLineEdit, QPushButton, QMessageBox
import bcrypt
import mysql.connector
from PyQt6.QtGui import QIntValidator,QIcon
import re
import uuid
from main import resource_path
from main_window import MainWindow
class RegistrationWindow(QDialog):
    def __init__(self,db_handler):
        super().__init__()
        self.setWindowTitle("Register")
        self.setFixedSize(400, 300)
        self.db_handler = db_handler

        icon_path = resource_path("assets/images/icon.ico")
        self.setWindowIcon(QIcon(icon_path))
        
        layout = QVBoxLayout()
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Full Name")
        layout.addWidget(self.username_input)
        
        self.email_input = QLineEdit()
        self.email_input.setPlaceholderText("Email")
        layout.addWidget(self.email_input)
        
        self.phone_input = QLineEdit()
        self.phone_input.setPlaceholderText("Phone No")
        int_validator = QIntValidator()
        self.phone_input.setValidator(int_validator)
        layout.addWidget(self.phone_input)

        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Password")
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        layout.addWidget(self.password_input)

        self.confirm_password_input = QLineEdit()
        self.confirm_password_input.setPlaceholderText("Confirm Password")
        self.confirm_password_input.setEchoMode(QLineEdit.EchoMode.Password)
        layout.addWidget(self.confirm_password_input)

        self.register_button = QPushButton("Register")
        self.register_button.clicked.connect(self.register_user)
        layout.addWidget(self.register_button)

        self.setLayout(layout)

    def register_user(self):
        username = self.username_input.text()
        email = self.email_input.text().strip()
        phone_no = self.phone_input.text().strip()
        password = self.password_input.text()
        confirm_password = self.confirm_password_input.text()

        if not username or not password or not confirm_password:
            QMessageBox.warning(self, "Error", "All fields are required.")
            return

        if password != confirm_password:
            QMessageBox.warning(self, "Error", "Passwords do not match.")
            return

        if not self.is_valid_email(email):
            QMessageBox.warning(self, "Error", "Invalid email format.")
            return

        if len(phone_no) < 10:  
            QMessageBox.warning(self, "Error", "Phone number must be at least 10 digits.")
            return
        
        try:
            user_id = str(uuid.uuid4())
            hashed_password = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
            self.save_to_database(user_id,username,email,phone_no, hashed_password)
            QMessageBox.information(self, "Success", "Registration successful!")
            self.accept()
            
        except Exception as e:
            QMessageBox.warning(self, "Error", str(e))

    def save_to_database(self,user_id, username,email,phone_no, hashed_password):
        connection = mysql.connector.connect(
            host="192.168.1.53", user="workcom", password="admin123", database="workcomposer"
        )
        cursor = connection.cursor()
        cursor.execute(
            "INSERT INTO users (user_id,username,email,phone_no, user_password) VALUES (%s,%s, %s, %s, %s)",
            (user_id,username,email,phone_no, hashed_password)
        )
        connection.commit()
        cursor.close()
        connection.close()
        
    def is_valid_email(self, email):
        email_regex = r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"
        return re.match(email_regex, email) is not None
    
