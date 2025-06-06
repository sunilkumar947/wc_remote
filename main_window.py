from datetime import datetime
from PyQt6.QtWidgets import QMainWindow, QVBoxLayout, QHBoxLayout, QWidget, QLabel, QFrame, QPushButton, QMessageBox
from PyQt6.QtCore import QDateTime, QTimer, Qt
from PyQt6.QtGui import QIcon, QFont
from date_time import DateTimeWidget
from login_time import LoginTimeWidget
from break_time import BreakWidget
from table import TableWidget
from screen_time import ScreenTimeWidget
from PyQt6.QtCore import QStandardPaths
from PIL import ImageGrab
import os
import winreg
import paramiko


def get_documents_path():
    documents_path = QStandardPaths.writableLocation(QStandardPaths.StandardLocation.DocumentsLocation)
    return documents_path
def upload_to_remote(local_path, screenshot_path, ssh_host, ssh_user, ssh_password):
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(ssh_host, username=ssh_user, password=ssh_password)

        sftp = ssh.open_sftp()
        
        # Ensure remote directory exists
        remote_dir = os.path.dirname(screenshot_path)
        try:
            sftp.stat(remote_dir)
        except IOError:
            # Directory does not exist, so create it recursively
            dirs = remote_dir.split('/')
            path = ''
            for dir in dirs:
                if dir:
                    path += f'/{dir}'
                    try:
                        sftp.stat(path)
                    except:
                        sftp.mkdir(path)

        sftp.put(local_path, screenshot_path)
        sftp.close()
        ssh.close()      
        
class MainWindow(QMainWindow):
    def __init__(self, icon_path, db_handler, user_id,username):
        super().__init__()
        print("MainWindow initialized.")

        self.screenshot_timer = QTimer(self)
        self.screenshot_timer.timeout.connect(self.take_screenshot)
        self.screenshot_timer.start(60000)    
        
        self.user_id = user_id
        self.username = username
        print(self.username,'???????????????????????????????')
        self.db_handler = db_handler
        self.setWindowTitle("Work Tracker")
        self.setWindowIcon(QIcon(icon_path))
        self.setGeometry(100, 100, 800, 600)
        self.setFixedSize(800, 600)

        central_widget = QWidget(self)
        central_widget.setStyleSheet("background-color: #2b2f38;") 
        self.setCentralWidget(central_widget)

        main_layout = QVBoxLayout(central_widget)
        username_layout = QVBoxLayout()
        header_layout = QHBoxLayout()
        login_break_layout = QHBoxLayout()

        # Title Label
        title_label = QLabel("Work Tracker Dashboard", self)
        title_label.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        title_label.setAlignment(Qt.AlignmentFlag.AlignLeft)
        title_label.setStyleSheet("color: white; padding: 10px;")
        
        # shows user name and id
        self.user_info_label = QLabel(f"User: {self.username} | ID: {self.user_id}", self)
        self.user_info_label.setFont(QFont("Arial", 10, QFont.Weight.Bold))
        self.user_info_label.setAlignment(Qt.AlignmentFlag.AlignLeft)
        self.user_info_label.setStyleSheet("color: white; padding: 10px;")

        # Logout Button
        self.logout_button = QPushButton("Logout", self)
        self.logout_button.setFont(QFont("Arial", 10, QFont.Weight.Bold))
        self.logout_button.setStyleSheet("""
            QPushButton {
                background-color: #d9534f;
                color: white;
                border-radius: 5px;
                padding: 5px 15px;
            }
            QPushButton:hover {
                background-color: #c9302c;
            }
        """)
        self.logout_button.clicked.connect(self.confirm_logout)

        # Add title and logout button to the header layout
        username_layout.addWidget(self.user_info_label)
        
        header_layout.addWidget(title_label)
        header_layout.addStretch()
        header_layout.addWidget(self.logout_button)
        

        # Divider Line
        divider = QFrame()
        divider.setFrameShape(QFrame.Shape.HLine)
        divider.setFrameShadow(QFrame.Shadow.Sunken)
        divider.setStyleSheet("background-color: #555; height: 2px;")

        self.date_time_widget = DateTimeWidget()
        self.break_widget = BreakWidget()
        self.screen_time_widget = ScreenTimeWidget(self.break_widget)
        self.login_time_widget = LoginTimeWidget(self.break_widget, self.screen_time_widget)
        self.table_widget = TableWidget()

        # Widget Styling
        widget_style = """
            QWidget {
                border-radius: 10px;
                border: 1px solid #555;
                background-color: #3d424b;
                color: white;
                padding: 5px;
            }
        """
        self.login_time_widget.setStyleSheet(widget_style)
        self.break_widget.setStyleSheet(widget_style)
        self.screen_time_widget.setStyleSheet(widget_style)
        self.table_widget.setStyleSheet("border-radius: 10px; background-color: #2f333b; color: white;")

        self.login_time_widget.setMinimumSize(200, 100)
        self.break_widget.setMinimumSize(200, 100)
        self.screen_time_widget.setMinimumSize(200, 100)

        login_break_layout.addWidget(self.login_time_widget)
        login_break_layout.addWidget(self.break_widget)
        login_break_layout.addWidget(self.screen_time_widget)

        main_layout.addLayout(username_layout)
        main_layout.addLayout(header_layout)
        main_layout.addWidget(divider)
        main_layout.addWidget(self.date_time_widget)
        main_layout.addLayout(login_break_layout)
        main_layout.addWidget(self.table_widget)

        main_layout.setContentsMargins(10, 10, 10, 10)
        login_break_layout.setContentsMargins(50, 0, 280, 0)
        login_break_layout.setSpacing(250)
        main_layout.setSpacing(10)

        # Timer to update data
        self.update_timer = QTimer(self)
        self.update_timer.timeout.connect(self.update_data)
        self.update_timer.start(60000)

    def update_data(self):
        """Update data in the database."""
        date, current_time = self.date_time_widget.get_date_time()
        login_time = self.login_time_widget.get_login_time()
        break_time = self.break_widget.get_break_time()
        screen_time = self.screen_time_widget.get_screen_time()

        self.db_handler.insert_data("work_time", [self.user_id, date, login_time, break_time, screen_time, current_time])
        print(f"Data updated: {date}, {login_time}, {screen_time}, {break_time}, {current_time}")

        app_usage_data = self.table_widget.get_table_data()
        for app_name, url, duration in app_usage_data:
            self.db_handler.insert_data("app_usage", [self.user_id, app_name, url, duration, date])
        print("App usage data updated.")

    def confirm_logout(self):
        """Shows a styled confirmation dialog before logging out."""
        msg_box = QMessageBox(self)
        msg_box.setWindowTitle("Confirm Logout")
        msg_box.setText("Are you sure you want to logout?")
        msg_box.setIcon(QMessageBox.Icon.Warning)

        # Apply dark theme styling to QMessageBox
        msg_box.setStyleSheet("""
            QMessageBox {
                background-color: #3a434d;
                color: white;
                border-radius: 10px;
                font-size: 12px;
            }
            QPushButton {
                border-radius: 5px;
                padding: 5px 15px;
                font-weight: bold;
            }
            QPushButton:hover {
                opacity: 0.9;
            }
        """)

        # Customize buttons
        yes_button = msg_box.addButton("Logout", QMessageBox.ButtonRole.AcceptRole)
        yes_button.setStyleSheet("background-color: #d9534f; color: white;")
        
        no_button = msg_box.addButton("Cancel", QMessageBox.ButtonRole.RejectRole)
        no_button.setStyleSheet("background-color: #555; color: white;")

        msg_box.exec()

        if msg_box.clickedButton() == yes_button:
            self.logout()

    def logout(self):
        """Handles user logout and application close."""
        logout_time = QDateTime.currentDateTime().toString("hh:mm:ss")
        self.login_time_widget.save_login_time(logout_time=logout_time)
        print(f"User logged out at {logout_time}. Closing application...")
        self.close()

    def closeEvent(self, event):
        """Handles application close event."""
        print("MainWindow is closing.")
        logout_time = QDateTime.currentDateTime().toString("hh:mm:ss")
        self.login_time_widget.save_login_time(logout_time=logout_time)
        print(f"Logout time: {logout_time}")
        event.accept()
        
    def get_onedrive_documents_path(self):
        """Fetch the OneDrive Documents folder path dynamically."""
        try:
            key = winreg.HKEY_CURRENT_USER
            sub_key = r"Software\Microsoft\OneDrive"
            with winreg.OpenKey(key, sub_key) as reg_key:
                onedrive_path, _ = winreg.QueryValueEx(reg_key, "UserFolder")
                print(f"Registry OneDrive Path: {onedrive_path}")
            # Append "Documents" to store in OneDrive/Documents
            documents_path = os.path.join(onedrive_path, "Documents")
            return documents_path
        except Exception as e:
            print(f"Error getting OneDrive path: {e}")
            return None
        
    
    def take_screenshot(self):
        try:
            # 1. Screenshot save locally first (temp)
            temp_local_path = os.path.join(os.getenv('TEMP'), "screenshot_temp.png")

            user_id = self.user_id  
            current_timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
            screenshot_name = f"screenshot_{current_timestamp}.png"

            screenshot = ImageGrab.grab()
            screenshot.save(temp_local_path)

            # 2. Define remote path on the server
            remote_folder = f"/home/workcom/screenshots/{user_id}/"
            screenshot_path = remote_folder + screenshot_name

            # 3. Upload to remote server
            upload_to_remote(
                local_path=temp_local_path,
                screenshot_path=screenshot_path,
                ssh_host="192.168.1.53",
                ssh_user="work-com",
                ssh_password="admin123"
            )
            

            print(f"Screenshot uploaded to remote server: {screenshot_path}")
            
            # 4. Save remote path to database
            self.db_handler.insert_data("screenshots", [self.user_id, screenshot_path, current_timestamp])

            # Optional: Delete local temp file
            if os.path.exists(temp_local_path):
                os.remove(temp_local_path)

        except Exception as e:
            print(f"Error while taking screenshot: {e}")
            
         
          
#################################################this below is for local save or one drive ###################################
    # def take_screenshot(self):
    #     try:
    #         onedrive_documents_path = self.get_onedrive_documents_path()
            
    #         if not onedrive_documents_path:
    #             print("OneDrive not found! Saving to local Documents folder instead.")
    #             onedrive_documents_path = get_documents_path()  # Fallback to local Documents

    #         user_id = self.user_id  
    #         screenshot_folder = os.path.join(onedrive_documents_path, "WorkTracker", "screenshots", user_id)
            
    #         if not os.path.exists(screenshot_folder):
    #             os.makedirs(screenshot_folder)

    #         current_timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
    #         screenshot_path = os.path.join(screenshot_folder, f"screenshot_{current_timestamp}.png")

    #         screenshot = ImageGrab.grab()
    #         screenshot.save(screenshot_path)
    #         print(f"Screenshot saved to {screenshot_path}")
    
    #     # Save to database      
    #         self.db_handler.insert_data("screenshots", [self.user_id, screenshot_path,current_timestamp])        

    #     except Exception as e:
    #         print(f"Error while taking screenshot: {e}")


    