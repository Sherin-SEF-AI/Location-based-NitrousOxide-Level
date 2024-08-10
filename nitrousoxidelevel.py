import sys
import http.client
import json
import csv
from datetime import datetime
import warnings
from PyQt5.QtWidgets import (QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
                             QTextEdit, QLineEdit, QComboBox, QMessageBox, QFileDialog, QTabWidget,
                             QGridLayout, QGroupBox)
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QFont, QPainter
from PyQt5.QtChart import QChart, QChartView, QLineSeries, QValueAxis, QDateTimeAxis

# Suppress DeprecationWarnings
warnings.filterwarnings("ignore", category=DeprecationWarning)

class LocationBasedNitrousOxideApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Advanced Nitrous Oxide Level Tracker')
        self.setGeometry(100, 100, 900, 700)
        self.location_history = []
        self.data_history = []
        self.auto_refresh_timer = QTimer(self)
        self.auto_refresh_timer.timeout.connect(self.auto_refresh)
        self.initUI()
        self.setStyleSheet("""
            QWidget {
                background-color: #f0f0f0;
                color: #333;
                font-size: 14px;
            }
            QPushButton {
                background-color: #4CAF50;
                color: white;
                padding: 5px 10px;
                border: none;
                border-radius: 3px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
            QLineEdit, QComboBox {
                padding: 5px;
                border: 1px solid #ddd;
                border-radius: 3px;
            }
            QTextEdit {
                border: 1px solid #ddd;
                border-radius: 3px;
            }
            QGroupBox {
                margin-top: 10px;
            }
        """)

    def initUI(self):
        main_layout = QVBoxLayout()

        # Header
        header_label = QLabel('Advanced Nitrous Oxide Level Tracker')
        header_label.setAlignment(Qt.AlignCenter)
        header_label.setFont(QFont('Arial', 18, QFont.Bold))
        header_label.setStyleSheet("color: #2C3E50; margin-bottom: 10px;")
        main_layout.addWidget(header_label)

        # Input section
        input_group = QGroupBox("Location Input")
        input_layout = QHBoxLayout()
        self.location_input = QLineEdit(self)
        self.location_input.setPlaceholderText('Enter a location')
        input_layout.addWidget(self.location_input)

        self.fetch_button = QPushButton('Fetch Data')
        self.fetch_button.clicked.connect(self.fetch_location_and_data)
        input_layout.addWidget(self.fetch_button)
        input_group.setLayout(input_layout)
        main_layout.addWidget(input_group)

        # Tab widget
        self.tab_widget = QTabWidget()
        main_layout.addWidget(self.tab_widget)

        # Results tab
        results_tab = QWidget()
        results_layout = QVBoxLayout()
        self.result_text = QTextEdit()
        self.result_text.setReadOnly(True)
        results_layout.addWidget(self.result_text)
        results_tab.setLayout(results_layout)
        self.tab_widget.addTab(results_tab, "Results")

        # Chart tab
        chart_tab = QWidget()
        chart_layout = QVBoxLayout()
        self.chart_view = QChartView()
        self.chart_view.setRenderHint(QPainter.Antialiasing)
        chart_layout.addWidget(self.chart_view)
        chart_tab.setLayout(chart_layout)
        self.tab_widget.addTab(chart_tab, "Chart")

        # Controls section
        controls_group = QGroupBox("Controls")
        controls_layout = QGridLayout()

        # Historical data section
        self.history_combo = QComboBox()
        self.history_combo.addItem("Select a previous location")
        controls_layout.addWidget(QLabel("History:"), 0, 0)
        controls_layout.addWidget(self.history_combo, 0, 1)

        self.load_history_button = QPushButton('Load')
        self.load_history_button.clicked.connect(self.load_historical_data)
        controls_layout.addWidget(self.load_history_button, 0, 2)

        # Export button
        self.export_button = QPushButton('Export Data')
        self.export_button.clicked.connect(self.export_data)
        controls_layout.addWidget(self.export_button, 1, 0)

        # Auto refresh
        self.auto_refresh_combo = QComboBox()
        self.auto_refresh_combo.addItems(['Auto Refresh Off', 'Every 5 minutes', 'Every 15 minutes', 'Every 30 minutes'])
        self.auto_refresh_combo.currentIndexChanged.connect(self.toggle_auto_refresh)
        controls_layout.addWidget(QLabel("Auto Refresh:"), 1, 1)
        controls_layout.addWidget(self.auto_refresh_combo, 1, 2)

        controls_group.setLayout(controls_layout)
        main_layout.addWidget(controls_group)

        self.setLayout(main_layout)

    def fetch_location_and_data(self):
        location_query = self.location_input.text()
        if location_query:
            self.result_text.setText("Fetching data...")
            QApplication.processEvents()  # Update GUI
            
            location = self.fetch_location(location_query)
            if location:
                nitrous_oxide_data = self.fetch_nitrous_oxide_data(location)
                self.display_results(location_query, location, nitrous_oxide_data)
                self.update_history(location_query)
                self.update_chart()
            else:
                self.result_text.setText("Failed to fetch location data.")
        else:
            QMessageBox.warning(self, "Input Error", "Please enter a location.")

    def fetch_location(self, location_query):
        try:
            conn = http.client.HTTPSConnection("map-geocoding.p.rapidapi.com")
            headers = {
                'x-rapidapi-key': "2d7198105fmsha78df4c828aea6ep182ce4jsn6a513052a904",
                'x-rapidapi-host': "map-geocoding.p.rapidapi.com"
            }
            formatted_location = location_query.replace(" ", "%20")
            conn.request("GET", f"/json?address={formatted_location}", headers=headers)
            res = conn.getresponse()
            data = res.read()
            location_data = json.loads(data.decode("utf-8"))

            self.result_text.append(f"Geocoding API Response:\n{json.dumps(location_data, indent=2)}\n\n")

            if location_data and "results" in location_data and len(location_data["results"]) > 0:
                geometry = location_data["results"][0]["geometry"]
                if "location" in geometry:
                    lat = geometry["location"].get("lat")
                    lng = geometry["location"].get("lng")
                    if lat and lng:
                        return f"{lat},{lng}"
            raise ValueError("Location data not found in API response")
        except Exception as e:
            self.result_text.append(f"Error fetching location: {str(e)}\n\n")
            return None

    def fetch_nitrous_oxide_data(self, location):
        try:
            conn = http.client.HTTPSConnection("atmosphere-nitrous-oxide-levels.p.rapidapi.com")
            headers = {
                'x-rapidapi-key': "2d7198105fmsha78df4c828aea6ep182ce4jsn6a513052a904",
                'x-rapidapi-host': "atmosphere-nitrous-oxide-levels.p.rapidapi.com"
            }
            conn.request("GET", f"/api/nitrous-oxide-api?location={location}", headers=headers)
            res = conn.getresponse()
            data = res.read()
            nitrous_oxide_data = json.loads(data.decode("utf-8"))
            
            self.result_text.append(f"Nitrous Oxide API Response:\n{json.dumps(nitrous_oxide_data, indent=2)}\n\n")
            
            return nitrous_oxide_data
        except Exception as e:
            self.result_text.append(f"Error fetching nitrous oxide data: {str(e)}\n\n")
            return None

    def display_results(self, location_query, location, nitrous_oxide_data):
        self.result_text.append(f"Processed Results:\n")
        self.result_text.append(f"Location Query: {location_query}\n")
        self.result_text.append(f"Geocoded Location: {location}\n\n")

        if nitrous_oxide_data:
            concentration = nitrous_oxide_data.get('concentration', 'N/A')
            measurement_time = nitrous_oxide_data.get('measurement_time', datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
            source = nitrous_oxide_data.get('source', 'N/A')

            structured_output = (
                f"Nitrous Oxide Levels:\n"
                f"  - Concentration: {concentration}\n"
                f"  - Measurement Time: {measurement_time}\n"
                f"  - Source: {source}\n"
            )

            self.result_text.append(structured_output)
            self.data_history.append({
                'location': location_query,
                'concentration': concentration,
                'measurement_time': measurement_time,
                'source': source
            })
        else:
            self.result_text.append("Failed to fetch or process Nitrous Oxide data.")

    def update_history(self, location):
        if location not in self.location_history:
            self.location_history.append(location)
            self.history_combo.addItem(location)

    def load_historical_data(self):
        selected_location = self.history_combo.currentText()
        if selected_location != "Select a previous location":
            self.location_input.setText(selected_location)
            self.fetch_location_and_data()

    def update_chart(self):
        series = QLineSeries()
        
        for idx, data in enumerate(self.data_history):
            if 'concentration' in data and data['concentration'] != 'N/A':
                try:
                    timestamp = datetime.strptime(data['measurement_time'], "%Y-%m-%d %H:%M:%S").timestamp() * 1000
                    concentration = float(data['concentration'])
                    series.append(timestamp, concentration)
                except ValueError:
                    print(f"Error parsing data point {idx}: {data}")
        
        chart = QChart()
        chart.addSeries(series)
        chart.setTitle("Nitrous Oxide Concentration Over Time")
        
        axis_x = QDateTimeAxis()
        axis_x.setTickCount(5)
        axis_x.setFormat("dd-MM-yyyy hh:mm")
        axis_x.setTitleText("Date")
        chart.addAxis(axis_x, Qt.AlignBottom)
        series.attachAxis(axis_x)
        
        axis_y = QValueAxis()
        axis_y.setTitleText("Concentration")
        chart.addAxis(axis_y, Qt.AlignLeft)
        series.attachAxis(axis_y)
        
        self.chart_view.setChart(chart)

    def export_data(self):
        if not self.data_history:
            QMessageBox.warning(self, "Export Error", "No data to export.")
            return

        file_name, _ = QFileDialog.getSaveFileName(self, "Save Data", "", "CSV Files (*.csv)")
        if file_name:
            with open(file_name, mode='w', newline='') as file:
                writer = csv.DictWriter(file, fieldnames=['location', 'concentration', 'measurement_time', 'source'])
                writer.writeheader()
                for data in self.data_history:
                    writer.writerow(data)
            QMessageBox.information(self, "Export Successful", f"Data exported to {file_name}")

    def toggle_auto_refresh(self, index):
        if index == 0:  # Auto Refresh Off
            self.auto_refresh_timer.stop()
        else:
            minutes = [5, 15, 30][index - 1]
            self.auto_refresh_timer.start(minutes * 60 * 1000)  # Convert minutes to milliseconds

    def auto_refresh(self):
        current_location = self.location_input.text()
        if current_location:
            self.fetch_location_and_data()

def main():
    app = QApplication(sys.argv)
    window = LocationBasedNitrousOxideApp()
    window.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
