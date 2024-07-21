# Imports
from PyQt5.QtCore import Qt, QDate
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QPushButton, QVBoxLayout, QHBoxLayout, QMessageBox, QTableWidget, QTableWidgetItem, QHeaderView, QCheckBox, QDateEdit, QLineEdit, QComboBox, QRadioButton, QButtonGroup
from PyQt5.QtSql import QSqlDatabase, QSqlQuery
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from sys import exit
import numpy as np
from collections import defaultdict
from datetime import datetime
import matplotlib.dates as mdates

# Main Class
class FitTrack(QWidget):
    def __init__(self):
        super().__init__()
        self.settings()
        self.initUI()
        self.button_click()
           
    # Settings
    def settings(self):
        self.setWindowTitle("FitTrack")
        self.resize(800,600)
        
    # init UI
    def initUI(self):
        # date
        self.date_box = QDateEdit()
        self.date_box.setDate(QDate.currentDate())
        
        # exercise type dropdown
        self.exercise_type_box = QComboBox()
        self.exercise_type_box.addItems(["Running", "Walking", "Cycling", "Swimming", "Other"])
        
        # calories box
        self.kal_box = QLineEdit()
        self.kal_box.setPlaceholderText("Number of Burned Calories")
        
        # distance counter
        self.distance_box = QLineEdit()
        self.distance_box.setPlaceholderText("Enter distance walked")
        
        # describe the exercise
        self.description = QLineEdit()
        self.description.setPlaceholderText("Enter a description")
        
        self.submit_btn = QPushButton("Submit")
        self.add_btn = QPushButton("Add")
        self.delete_btn = QPushButton("Delete")
        self.clear_btn = QPushButton("Clear")
        self.dark_mode = QCheckBox("Dark Mode")

        self.calories_radio = QRadioButton("Calories Over Time")
        self.distance_radio = QRadioButton("Distance Over Time")
        self.calories_radio.setChecked(True)
        self.graph_type_group = QButtonGroup()
        self.graph_type_group.addButton(self.calories_radio)
        self.graph_type_group.addButton(self.distance_radio)
        
        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels(["Id","Date","Exercise Type","Calories","Distance","Description"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        
        self.figure = plt.figure()
        self.canvas = FigureCanvas(self.figure)
        
        # Design Our Layout
        self.master_layout = QHBoxLayout()
        self.col1 = QVBoxLayout()
        self.col2 = QVBoxLayout()
        
        self.sub_row1 = QHBoxLayout()
        self.sub_row2 = QHBoxLayout()
        self.sub_row3 = QHBoxLayout()
        self.sub_row4 = QHBoxLayout()
        self.sub_row5 = QHBoxLayout()
        
        self.sub_row1.addWidget(QLabel("Date:"))
        self.sub_row1.addWidget(self.date_box)
        self.sub_row2.addWidget(QLabel("Exercise Type:"))
        self.sub_row2.addWidget(self.exercise_type_box)
        self.sub_row3.addWidget(QLabel("Calories:"))
        self.sub_row3.addWidget(self.kal_box)
        self.sub_row4.addWidget(QLabel("KM:"))
        self.sub_row4.addWidget(self.distance_box)
        self.sub_row5.addWidget(QLabel("Description:"))
        self.sub_row5.addWidget(self.description)
        
        self.col1.addLayout(self.sub_row1)
        self.col1.addLayout(self.sub_row2)
        self.col1.addLayout(self.sub_row3)
        self.col1.addLayout(self.sub_row4)
        self.col1.addLayout(self.sub_row5)
        self.col1.addWidget(self.dark_mode)
        self.col1.addWidget(self.calories_radio)
        self.col1.addWidget(self.distance_radio)
        
        btn_row1 = QHBoxLayout()
        btn_row2 = QHBoxLayout()
        
        btn_row1.addWidget(self.add_btn)
        btn_row1.addWidget(self.delete_btn)
        btn_row2.addWidget(self.submit_btn)
        btn_row2.addWidget(self.clear_btn)
        
        self.col1.addLayout(btn_row1)
        self.col1.addLayout(btn_row2)
        
        self.col2.addWidget(self.canvas)
        self.col2.addWidget(self.table)
        
        self.master_layout.addLayout(self.col1, 30)
        self.master_layout.addLayout(self.col2, 70)
        self.setLayout(self.master_layout)
        
        self.apply_styles()
        self.load_table()
     
    #Events
    def button_click(self):
        self.add_btn.clicked.connect(self.add_workout)
        self.delete_btn.clicked.connect(self.delete_workout)
        self.submit_btn.clicked.connect(self.update_graph)
        self.dark_mode.stateChanged.connect(self.toggle_dark)
        self.clear_btn.clicked.connect(self.reset)
        self.calories_radio.toggled.connect(self.update_graph)
        self.distance_radio.toggled.connect(self.update_graph)
    
    # Load Tables
    def load_table(self):
        self.table.setRowCount(0)
        query = QSqlQuery("SELECT * FROM fitness ORDER BY date DESC")
        row = 0
        while query.next():
            fit_id = query.value(0)
            date = query.value(1)
            exercise_type = query.value(2)
            calories = query.value(3)
            distance = query.value(4)
            description = query.value(5)
            
            self.table.insertRow(row)
            self.table.setItem(row, 0, QTableWidgetItem(str(fit_id)))
            self.table.setItem(row, 1, QTableWidgetItem(date))
            self.table.setItem(row, 2, QTableWidgetItem(exercise_type))
            self.table.setItem(row, 3, QTableWidgetItem(str(calories)))
            self.table.setItem(row, 4, QTableWidgetItem(str(distance)))
            self.table.setItem(row, 5, QTableWidgetItem(description))
            row += 1
            
    # Add Tables
    def add_workout(self):
        date = self.date_box.date().toString("yyyy-MM-dd")
        exercise_type = self.exercise_type_box.currentText()
        calories = self.kal_box.text()
        distance = self.distance_box.text()
        description = self.description.text()
        
        query = QSqlQuery()
        query.prepare("""
                      INSERT INTO fitness (date, exercise_type, calories, distance, description) 
                      VALUES (?, ?, ?, ?, ?)
                      """)
        query.addBindValue(date)
        query.addBindValue(exercise_type)
        query.addBindValue(calories)
        query.addBindValue(distance)
        query.addBindValue(description)
        
        if not query.exec_():
            print(f"Error adding workout: {query.lastError().text()}")
            QMessageBox.warning(self, "Error", f"Could not add workout: {query.lastError().text()}")
        else:
            self.date_box.setDate(QDate.currentDate())
            self.kal_box.clear()
            self.distance_box.clear()
            self.description.clear()
            self.load_table()
            self.update_graph()
        
    # Delete Tables
    def delete_workout(self):
        selected_row = self.table.currentRow()
        
        if selected_row == -1:
            QMessageBox.warning(self,"Error","Please choose a row to delete")
            return
            
        fit_id = int(self.table.item(selected_row,0).text())
        confirm = QMessageBox.question(self,"Are you sure?", "Delete this workout", QMessageBox.Yes | QMessageBox.No)
        
        if confirm == QMessageBox.No:
            return
        
        query = QSqlQuery()
        query.prepare("DELETE FROM fitness WHERE id = ?")
        query.addBindValue(fit_id)
        if not query.exec_():
            print(f"Error deleting workout: {query.lastError().text()}")
            QMessageBox.warning(self, "Error", f"Could not delete workout: {query.lastError().text()}")
        
        self.load_table()
        self.update_graph()
    
    # Update Graph
    def update_graph(self):
        if self.calories_radio.isChecked():
            self.plot_calories()
        elif self.distance_radio.isChecked():
            self.plot_distance()
    
    # Plot Calories
    def plot_calories(self):
        date_calories = defaultdict(float)

        query = QSqlQuery("SELECT date, calories FROM fitness ORDER BY date ASC")
        while query.next():
            date = query.value(0)
            calorie = query.value(1)
            date_calories[date] += calorie

        dates = [datetime.strptime(date, '%Y-%m-%d') for date in date_calories.keys()]
        calories = list(date_calories.values())

        try:
            self.figure.clear()
            ax = self.figure.add_subplot(111)
            ax.plot(dates, calories, marker='o', linestyle='-', color='b', label='Calories Burned')
            ax.set_title("Calories Burned Over Time")
            ax.set_xlabel("Date")
            ax.set_ylabel("Calories")
            ax.legend()
            ax.grid(True)
            ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
            ax.xaxis.set_major_locator(mdates.DayLocator(interval=7))  
            #plt.setp(ax.get_xticklabels(), rotation=45, ha='right')  

            self.canvas.draw()

        except Exception as e:
            print(f"ERROR: {e}")
            QMessageBox.warning(self, "Error", "Please enter some data first!")

# Plot Distance
    def plot_distance(self):
        date_distance = defaultdict(float)

        query = QSqlQuery("SELECT date, distance FROM fitness ORDER BY date ASC")
        while query.next():
            date = query.value(0)
            distance = query.value(1)
            date_distance[date] += distance

        dates = [datetime.strptime(date, '%Y-%m-%d') for date in date_distance.keys()]
        distances = list(date_distance.values())

        try:
            self.figure.clear()
            ax = self.figure.add_subplot(111)
            ax.plot(dates, distances, marker='o', linestyle='-', color='g', label='Distance Covered')
            ax.set_title("Distance Covered Over Time")
            ax.set_xlabel("Date")
            ax.set_ylabel("Distance (KM)")
            ax.legend()
            ax.grid(True)
            ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
            ax.xaxis.set_major_locator(mdates.DayLocator(interval=7))  
            #plt.setp(ax.get_xticklabels(), rotation=45, ha='right')  

            self.canvas.draw()

        except Exception as e:
            print(f"ERROR: {e}")
            QMessageBox.warning(self, "Error", "Please enter some data first!")
        
    def apply_styles(self):
        self.setStyleSheet("""
            QWidget {
                background-color: #b8c9e1;
            }

            QLabel {
                color: #333;
                font-size: 14px;
            }

            QLineEdit, QComboBox, QDateEdit {
                background-color: #b8c9e1;
                color: #333;
                border: 1px solid #444;
                padding: 5px;
            }

            QTableWidget {
                background-color: #b8c9e1;
                color: #333;
                border: 1px solid #444;
                selection-background-color: #ddd;
            }

            QPushButton {
                background-color: #4caf50;
                color: #fff;
                border: none;
                padding: 8px 16px;
                font-size: 14px;
            }

            QPushButton:hover {
                background-color: #45a049;
            }

            QRadioButton {
                font-size: 14px;
                color: #333;
            }

            QCheckBox {
                color: #333;
            }
        """)
        figure_color = "#b8c9e1"
        self.figure.patch.set_facecolor(figure_color)
        self.canvas.setStyleSheet(f"background-color:{figure_color}")

        if self.dark_mode.isChecked():
            self.setStyleSheet("""
                QWidget {
                    background-color: #222222;
                }

                QLabel {
                    color: #eeeeee;
                    font-size: 14px;
                }

                QLineEdit, QComboBox, QDateEdit {
                    background-color: #222222;
                    color: #eeeeee;
                    border: 1px solid #444;
                    padding: 5px;
                }

                QTableWidget {
                    background-color: #444444;
                    color: #eeeeee;
                    border: 1px solid #444;
                    selection-background-color: #555555;
                }

                QPushButton {
                    background-color: #40484c;
                    color: #fff;
                    border: none;
                    padding: 8px 16px;
                    font-size: 14px;
                }

                QPushButton:hover {
                    background-color: #444d4f;
                }

                QRadioButton {
                    color: #eeeeee;
                    font-size: 14px;
                }

                QCheckBox {
                    color: #eeeeee;
                }
            """)
            figure_color = "#40484c"
            self.figure.patch.set_facecolor(figure_color)
            self.canvas.setStyleSheet(f"background-color:{figure_color}")
        
        
    # Dark Mode
    def toggle_dark(self):
        self.apply_styles()
    
    # Reset
    def reset(self):
        self.date_box.setDate(QDate.currentDate())
        self.kal_box.clear()
        self.distance_box.clear()
        self.description.clear()
        self.figure.clear()
        self.canvas.draw()

    
# Initialize my DB
db = QSqlDatabase.addDatabase("QSQLITE")
db.setDatabaseName("fitness.db")

if not db.open():
    QMessageBox.critical(None,"ERROR","Cannot open the Database")
    exit(2)
    
query = QSqlQuery()
query.exec_("""
            CREATE TABLE IF NOT EXISTS fitness (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date TEXT,
                exercise_type TEXT,
                calories REAL,
                distance REAL,
                description TEXT
            )
            """)

if __name__ == "__main__":
    app = QApplication([])
    main = FitTrack()
    main.show()
    app.exec_()
