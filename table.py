from PyQt6.QtWidgets import QTableWidget, QTableWidgetItem, QAbstractScrollArea, QSizePolicy, QVBoxLayout, QWidget, QHeaderView
from PyQt6.QtCore import QThread, pyqtSignal, QStandardPaths, Qt
from win32gui import GetForegroundWindow
import win32com.client as win32
from win32process import GetWindowThreadProcessId
import psutil
import time
import os
import xlsxwriter
from pywinauto import Application
from pywinauto.findwindows import find_elements


def get_documents_path():
    return QStandardPaths.writableLocation(QStandardPaths.StandardLocation.DocumentsLocation)


class AppTrackerThread(QThread):
    update_signal = pyqtSignal(str, int, str)  # app_name, duration, url

    def __init__(self):
        super().__init__()
        self.running = True
        self.app_durations = {}  # {app_name: seconds}
        self.app_urls = {}       # {app_name: last_known_url}

    def convert_duration_to_time_format(self, duration_in_seconds):
        hours = duration_in_seconds // 3600
        minutes = (duration_in_seconds % 3600) // 60
        seconds = duration_in_seconds % 60
        return f"{hours:02}:{minutes:02}:{seconds:02}"

    def get_chrome_url(self):
        try:
            elements = find_elements(title_re=".*Chrome.*", backend="uia")
            if not elements:
                return "N/A"

            handle = elements[0].handle
            app = Application(backend='uia').connect(handle=handle)
            dlg = app.top_window()

            url_element = dlg.child_window(title="Address and search bar", control_type="Edit")
            url = url_element.get_value()
            return url if url else "N/A"
        except Exception:
            return "N/A"

    def run(self):
        start_time = time.time()
        while self.running:
            hwnd = GetForegroundWindow()
            if hwnd == 0:
                time.sleep(1)
                continue

            try:
                _, pid = GetWindowThreadProcessId(hwnd)
                if pid <= 0:
                    raise ValueError(f"Invalid PID: {pid}")
                app_name = psutil.Process(pid).name()
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess, ValueError):
                app_name = "Unknown"

            if app_name not in self.app_durations:
                self.app_durations[app_name] = 0
            self.app_durations[app_name] += 1

            # Get URL only for Chrome
            if "chrome" in app_name.lower():
                url = self.get_chrome_url()
                self.app_urls[app_name] = url
            else:
                url = self.app_urls.get(app_name, "N/A")

            self.update_signal.emit(app_name, self.app_durations[app_name], url)

            if time.time() - start_time >= 60:
                self.save_to_excel()
                start_time = time.time()

            time.sleep(1)

    def close_excel_if_open(self):
        current_date = time.strftime("%Y-%m-%d")
        file_name = f"app_tracking_{current_date}.xlsx"
        documents_path = get_documents_path()
        folder_path = os.path.join(documents_path, "AppTracker", "logs")
        file_path = os.path.join(folder_path, file_name)

        for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
            try:
                if 'excel' in proc.info['name'].lower() and any(file_path.lower() in arg.lower() for arg in proc.info['cmdline']):
                    proc.terminate()
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass

    def save_to_excel(self):
        self.close_excel_if_open()
        current_date = time.strftime("%Y-%m-%d")
        documents_path = get_documents_path()
        folder_path = os.path.join(documents_path, "AppTracker", "logs")
        if not os.path.exists(folder_path):
            os.makedirs(folder_path)
        file_path = os.path.join(folder_path, f"app_tracking_{current_date}.xlsx")

        try:
            workbook = xlsxwriter.Workbook(file_path)
            worksheet = workbook.add_worksheet()

            worksheet.write('A1', 'App')
            worksheet.write('B1', 'URL')
            worksheet.write('C1', 'Duration (HH:MM:SS)')

            for row, (app_name, duration) in enumerate(self.app_durations.items(), start=1):
                formatted_duration = self.convert_duration_to_time_format(duration)
                url = self.app_urls.get(app_name, "N/A")
                worksheet.write(row, 0, app_name)
                worksheet.write(row, 1, url)
                worksheet.write(row, 2, formatted_duration)

            workbook.close()

            excel = win32.Dispatch("Excel.Application")
            excel.Visible = False
            excel.DisplayAlerts = False

            workbook = excel.Workbooks.Open(file_path)
            workbook.Password = "123456"
            workbook.Save()
            workbook.Close()
            excel.Quit()
        except Exception as e:
            print(f"Error saving Excel file: {e}")

    def stop(self):
        self.running = False
        self.wait()


class TableWidget(QWidget):
    def __init__(self):
        super().__init__()

        self.table = QTableWidget(self)
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["S.No", "Apps", "Url", "Duration"])
        self.update_table_rows()
        self.table.setStyleSheet("background-color: #717d8a;")
        self.table.verticalHeader().setVisible(False)
        self.table.horizontalHeader().setStyleSheet("""
            QHeaderView::section {
                color: white;
                background-color: #2C3E50;
                font-weight: bold;
                font-size: 14px;
                padding: 5px;
            }
        """)
        self.table.setColumnWidth(0, 36)
        self.table.setColumnWidth(1, 240)
        self.table.setColumnWidth(2, 404)
        self.table.setColumnWidth(3, 79)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Fixed)

        self.table.setMinimumHeight(100)
        self.table.setMinimumWidth(600)
        self.table.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.table.setSizeAdjustPolicy(QAbstractScrollArea.SizeAdjustPolicy.AdjustToContents)
        self.table.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.table.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)

        self.table.verticalScrollBar().setStyleSheet("""
            QScrollBar:vertical {
                background: #2C3E50;
                width: 10px;
            }
            QScrollBar::handle:vertical {
                background: #95A5A6;
                min-height: 20px;
                border-radius: 4px;
            }
            QScrollBar::handle:vertical:hover {
                background: #BDC3C7;
            }
        """)
        self.table.horizontalScrollBar().setStyleSheet("""
            QScrollBar:horizontal {
                background: #2C3E50;
                height: 10px;
            }
            QScrollBar::handle:horizontal {
                background: #95A5A6;
                min-width: 20px;
                border-radius: 4px;
            }
            QScrollBar::handle:horizontal:hover {
                background: #BDC3C7;
            }
        """)

        layout = QVBoxLayout(self)
        layout.addWidget(self.table)

        self.tracker_thread = AppTrackerThread()
        self.tracker_thread.update_signal.connect(self.update_table)
        self.tracker_thread.start()

    def update_table_rows(self):
        self.table.setRowCount(0)

    def update_table(self, app_name, duration, url):
        formatted_duration = self.tracker_thread.convert_duration_to_time_format(duration)
        for row in range(self.table.rowCount()):
            if self.table.item(row, 1) and self.table.item(row, 1).text() == app_name:
                self.table.setItem(row, 2, QTableWidgetItem(url))
                self.table.setItem(row, 3, QTableWidgetItem(formatted_duration))
                return
        row = self.table.rowCount()
        self.table.insertRow(row)
        self.table.setItem(row, 0, QTableWidgetItem(str(row + 1)))
        self.table.setItem(row, 1, QTableWidgetItem(app_name))
        self.table.setItem(row, 2, QTableWidgetItem(url))
        self.table.setItem(row, 3, QTableWidgetItem(formatted_duration))


        
    def get_table_data(self):
        table_data = []
        for row in range(self.table.rowCount()):
            app_name = self.table.item(row, 1).text()
            duration = self.table.item(row, 3).text()
            url=self.table.item(row,2).text()
            table_data.append((app_name, url, duration))  
        return table_data
            
        
    def setRowBackgroundColor(self, row, color):
        for column in range(self.table.columnCount()):
            item = self.table.item(row, column)
            if item is not None:
                item.setBackground(color)

    def closeEvent(self, event):
        self.tracker_thread.stop()
        super().closeEvent(event)