import sys
import sqlite3
import smtplib
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                             QLabel, QLineEdit, QPushButton, QMessageBox, 
                             QTableWidget, QTableWidgetItem, QAbstractItemView, QCalendarWidget)
from PyQt5.QtCore import Qt, QDate, QTimer, QTime
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import QComboBox
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText



class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()
        self.selected_task = None  # Initialize selected_task
        self.last_deleted_task = None  # Initialize last_deleted_task
        self.active_table = None  # Track which table has the selected task

    def initUI(self):
        self.setWindowTitle('Calendar with Tasks')
        self.setGeometry(100, 100, 1200, 600)  # Adjusted width

        # Main layout
        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)

        # Calendar widget
        self.calendar = QCalendarWidget(self)
        self.calendar.setFixedHeight(400)  # Set the height to make it taller
        self.calendar.selectionChanged.connect(self.load_tasks)
        layout.addWidget(self.calendar)

        # Buttons for task actions
        button_layout = QHBoxLayout()
        
        # Complete Task Button
        self.complete_task_button = QPushButton('Complete Task', self)
        self.complete_task_button.setFixedHeight(50)
        self.complete_task_button.clicked.connect(self.complete_task)
        button_layout.addWidget(self.complete_task_button)

        # Undo Task Button
        self.undo_task_button = QPushButton('Undo Last Deletion', self)
        self.undo_task_button.setFixedHeight(50)
        self.undo_task_button.clicked.connect(self.undo_last_deletion)
        button_layout.addWidget(self.undo_task_button)

        # Today Button
        today_button = QPushButton('Today', self)
        today_button.setFixedHeight(50)
        today_button.clicked.connect(self.go_to_today)
        button_layout.addWidget(today_button)

        layout.addLayout(button_layout)

        # Date and task input area
        input_layout = QHBoxLayout()
        
        # Date and task count display
        self.task_count_label = QLabel('Total Tasks: ', self)






       # self.current_time = QLabel(QTime.currentTime())






        # Set font size for labels
        font = QFont()
        font.setPointSize(16)
        self.task_count_label.setFont(font)

        input_layout.addWidget(self.task_count_label)

        # Database selection dropdown (moved here)
        self.db_selector = QComboBox(self)
        self.db_selector.addItems(["Matthew", "Jorge", "Tim"])
        self.db_selector.setFixedWidth(200)  
        self.db_selector.setFixedHeight(30)
        self.db_selector.currentIndexChanged.connect(self.switch_database)
        input_layout.addWidget(self.db_selector)

        # Add Task Input
        self.task_input = QLineEdit(self)
        self.task_input.setFixedHeight(50)
        self.task_input.setFixedWidth(600)
        self.task_input.setPlaceholderText('Enter a new task')
        input_layout.addWidget(self.task_input)

        # Add Task Button
        self.add_task_button = QPushButton('Add Task', self)
        self.add_task_button.setFixedHeight(50)
        self.add_task_button.setFixedWidth(200)
        self.add_task_button.clicked.connect(self.add_task)
        input_layout.addWidget(self.add_task_button)

        layout.addLayout(input_layout)

        # Send Email Button
        send_email_button = QPushButton('Send Email', self)
        send_email_button.setFixedHeight(50)
        send_email_button.clicked.connect(self.send_daily_email)
        button_layout.addWidget(send_email_button)

        # Table layout for tasks
        table_layout = QHBoxLayout()

        # Define consistent width for tables
        table_width = 700  # Set the width to 500

        # Vertical layout for tasks on selected date
        selected_date_layout = QVBoxLayout()
        left_table_title = QLabel('', self)
        date = self.calendar.selectedDate().toPyDate()
        left_table_title.setText('Tasks on selected date:')
        
        # Set font size for table title
        font.setPointSize(16)
        left_table_title.setFont(font)
        
        selected_date_layout.addWidget(left_table_title)
        self.selected_date_table = QTableWidget(self)
        self.selected_date_table.setFixedWidth(table_width)  # Set width to 500
        self.selected_date_table.setColumnCount(2)
        self.selected_date_table.setHorizontalHeaderLabels(['Task', 'Date'])
        self.selected_date_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.selected_date_table.itemSelectionChanged.connect(self.table_item_selected)
        self.selected_date_table.setStyleSheet('QTableWidget { border: 2px solid blue; }')  # Blue border
        selected_date_layout.addWidget(self.selected_date_table)
        table_layout.addLayout(selected_date_layout)

        # Vertical layout for total tasks
        total_tasks_layout = QVBoxLayout()
        right_table_title = QLabel('Total Tasks:', self)
        
        # Set font size for table title
        font.setPointSize(16)
        right_table_title.setFont(font)
        
        total_tasks_layout.addWidget(right_table_title)
        self.total_tasks_table = QTableWidget(self)
        self.total_tasks_table.setFixedWidth(table_width)  # Set width to 500
        self.total_tasks_table.setColumnCount(2)
        self.total_tasks_table.setHorizontalHeaderLabels(['Task', 'Date'])
        self.total_tasks_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.total_tasks_table.itemSelectionChanged.connect(self.table_item_selected)
        self.total_tasks_table.itemDoubleClicked.connect(self.table_item_double_clicked)  # Connect double-click event
        self.total_tasks_table.setStyleSheet('QTableWidget { border: 2px solid blue; }')  # Blue border
        total_tasks_layout.addWidget(self.total_tasks_table)
        table_layout.addLayout(total_tasks_layout)

        layout.addLayout(table_layout)

        # Setup database
        self.databasePath = 'tim.db'
        self.setup_database()
        self.databasePath = 'matthew.db'
        self.setup_database()

        # Load tasks for today's date and all tasks
        self.load_tasks()
        self.load_all_tasks()

        #Set up a timer to send an emaily daily
        self.email_timer = QTimer(self)
        self.email_timer.timeout.connect(self.check_time_for_email)
        self.email_timer.start(60000) #checks every min

##################################################################################################################

    

    def setup_database(self):
        db = sqlite3.connect(self.databasePath)
        cursor = db.cursor()
        
        # Create table with the correct schema
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                task TEXT NOT NULL,
                date TEXT NOT NULL,
                completed INTEGER NOT NULL DEFAULT 0
            )
        ''')
        
        # Ensure the 'completed' column exists
        cursor.execute('''
            PRAGMA table_info(tasks);
        ''')
        columns = cursor.fetchall()
        column_names = [column[1] for column in columns]
        if 'completed' not in column_names:
            cursor.execute('ALTER TABLE tasks ADD COLUMN completed INTEGER NOT NULL DEFAULT 0')
        
        db.commit()
        db.close()

    def load_tasks(self):
        date = self.calendar.selectedDate().toPyDate()
        
        self.selected_date_table.setRowCount(0)  # Clear existing rows
        
        db = sqlite3.connect(self.databasePath)
        cursor = db.cursor()
        query = "SELECT task FROM tasks WHERE date = ? AND completed = 0"
        results = cursor.execute(query, (date,)).fetchall()
        for row_index, result in enumerate(results):
            self.selected_date_table.insertRow(row_index)
            self.selected_date_table.setItem(row_index, 0, QTableWidgetItem(result[0]))
            self.selected_date_table.setItem(row_index, 1, QTableWidgetItem(str(date)))
        self.selected_date_table.resizeColumnsToContents()  # Resize columns to fit contents
        db.close()

        self.update_task_count()  # Update task count after loading tasks

    def update_task_count(self):
        date = self.calendar.selectedDate().toPyDate()
        db = sqlite3.connect(self.databasePath)
        cursor = db.cursor()
        query = "SELECT COUNT(*) FROM tasks WHERE date = ? AND completed = 0"
        count = cursor.execute(query, (date,)).fetchone()[0]
        self.task_count_label.setText(f'Total Tasks: {count}')
        db.close()

    def add_task(self):
        new_task = self.task_input.text()
        if not new_task:
            QMessageBox.warning(self, 'No Task Entered', 'Please enter a task.')
            return
        
        date = self.calendar.selectedDate().toPyDate()
        db = sqlite3.connect(self.databasePath)
        cursor = db.cursor()
        query = "INSERT INTO tasks (task, date) VALUES (?, ?)"
        cursor.execute(query, (new_task, date))
        db.commit()
        db.close()
        
        self.task_input.clear()
        self.load_tasks()
        self.load_all_tasks()

    def complete_task(self):
        if self.selected_task and self.active_table:
            task_text = self.selected_task
            date = self.active_table.item(self.active_table.currentRow(), 1).text()

            # Capture the last deleted task
            self.last_deleted_task = (task_text, date)

            # Update task status in the database
            db = sqlite3.connect(self.databasePath)
            cursor = db.cursor()
            query = "DELETE FROM tasks WHERE task = ? AND date = ?"
            cursor.execute(query, (task_text, date))
            db.commit()
            db.close()

            # Remove the task from both tables
            self.remove_task_from_table(self.selected_date_table, task_text, date)
            self.remove_task_from_table(self.total_tasks_table, task_text, date)

            # Update the task list
            self.load_tasks()
            self.load_all_tasks()
        else:
            QMessageBox.warning(self, 'No Task Selected', 'Please select a task to complete.')

    def remove_task_from_table(self, table, task_text, date):
        for row in range(table.rowCount()):
            if (table.item(row, 0).text() == task_text and table.item(row, 1).text() == date):
                table.removeRow(row)
                break

    def load_all_tasks(self):
        db = sqlite3.connect(self.databasePath)
        cursor = db.cursor()
        query = "SELECT task, date FROM tasks WHERE completed = 0"
        results = cursor.execute(query).fetchall()
        db.close()

        self.total_tasks_table.setRowCount(0)  # Clear existing rows

        for row_index, (task, date) in enumerate(results):
            self.total_tasks_table.insertRow(row_index)
            self.total_tasks_table.setItem(row_index, 0, QTableWidgetItem(task))
            self.total_tasks_table.setItem(row_index, 1, QTableWidgetItem(date))
        self.total_tasks_table.resizeColumnsToContents()  # Resize columns to fit contents

    def go_to_today(self):
        today = QDate.currentDate()
        self.calendar.setSelectedDate(today)
        self.load_tasks()

    def table_item_selected(self):
        # Track the table and the selected task
        table = self.sender()
        if table.selectedItems():
            self.selected_task = table.selectedItems()[0].text()
            self.active_table = table

    def table_item_double_clicked(self, item):
        # Get the row of the double-clicked item
        row = item.row()

        # Determine which table was double-clicked
        if self.active_table == self.selected_date_table:
            date_str = self.selected_date_table.item(row, 1).text()
        elif self.active_table == self.total_tasks_table:
            date_str = self.total_tasks_table.item(row, 1).text()
        else:
            return

        # Convert the date string to QDate
        selected_date = QDate.fromString(date_str, 'yyyy-MM-dd')

        # Set the calendar to the selected date
        self.calendar.setSelectedDate(selected_date)

        # Load tasks for the newly selected date
        self.load_tasks()


    def undo_last_deletion(self):
        if self.last_deleted_task:
            task_text, date = self.last_deleted_task
            db = sqlite3.connect(self.databasePath)
            cursor = db.cursor()
            query = "INSERT INTO tasks (task, date) VALUES (?, ?)"
            cursor.execute(query, (task_text, date))
            db.commit()
            db.close()

            self.last_deleted_task = None  # Clear the last deleted task

            self.load_tasks()
            self.load_all_tasks()
        else:
            QMessageBox.warning(self, 'No Deletion to Undo', 'There is no deleted task to undo.')

    def switch_database(self):
        selected_db = self.db_selector.currentText().lower() + '.db'
        self.databasePath = selected_db
        self.setup_database()  # Ensure the table exists in the new database
        self.load_tasks()
        self.load_all_tasks()

    def closeEvent(self, event):
        response = QMessageBox.question(self, 'Quit Application',
                                        'Are you sure you want to quit?',
                                        QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if response == QMessageBox.Yes:
            event.accept()
        else:
            event.ignore()

    #Send automated Email
    def send_daily_email(self):
        emailUser = "email@gmail.com"  #enter your own email

        msg = MIMEMultipart('alternative')
        msg['Subject'] = "Daily Task Reminder"
        msg['From'] = emailUser
        msg['To'] = emailUser

        total_tasks = ""
        uncompleted_tasks = ""
        total_task_count = 0
        uncompleted_task_count = 0

        db = sqlite3.connect(self.databasePath)
        cursor = db.cursor()
        query = "SELECT task, date, completed FROM tasks"
        results = cursor.execute(query).fetchall()
        db.close()

        for result in results:
            task, date, completed = result
            total_task_count += 1
            total_tasks += f"{task} (Due: {date})\n"
            if not completed:
                uncompleted_task_count += 1
                uncompleted_tasks += f"{task} (Due: {date})\n"

        body = f"You have {total_task_count} tasks in total.\n\n" \
               f"Total Tasks:\n{total_tasks}\n" \
               

        msg.attach(MIMEText(body, 'plain'))

        s = smtplib.SMTP('smtp.ad.cirrus.com')
        s.sendmail(msg['From'], [msg['To']], msg.as_string())
        s.quit()

        print("Email sent successfully!")

    def check_time_for_email(self):
        current_time = QTime.currentTime()
        print(current_time)
        email_time = QTime(14, 25)
        if current_time.hour() == email_time.hour():
            print("correct hour")
            if current_time.minute() == email_time.minute():
                print("correct minute")
                self.send_daily_email()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    mainWin = MainWindow()
    mainWin.show()
    sys.exit(app.exec_())
