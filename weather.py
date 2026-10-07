import sys
import requests
from PyQt5 import QtCore, QtGui, QtWidgets


API_KEY = "57b9f012ac9c8fbbf3f2dc655e5dfaf5"
GEO_URL = "http://api.openweathermap.org/geo/1.0/direct"
WEATHER_URL = "https://api.openweathermap.org/data/2.5/weather"


class WeatherAPI:
    def __init__(self, api_key=API_KEY):
        self.api_key = api_key

    def get_coords(self, city):
        try:
            res = requests.get(
                GEO_URL,
                params={"q": city, "limit": 1, "appid": self.api_key},
                timeout=5,
            )
            if res.status_code == 200:
                data = res.json()
                if data:
                    return data[0]
            return None
        except requests.exceptions.RequestException as e:
            print("Geo API error:", e)
            return None

    def get_weather(self, lat, lon):
        try:
            res = requests.get(
                WEATHER_URL,
                params={
                    "lat": lat,
                    "lon": lon,
                    "appid": self.api_key,
                    "units": "metric",
                },
                timeout=5,
            )
            if res.status_code == 200:
                return res.json()
            return None
        except requests.exceptions.RequestException as e:
            print("Weather API error:", e)
            return None


class Ui_WeatherWindow(object):
    def setupUi(self, MainWindow):
        self.MainWindow = MainWindow
        self.api = WeatherAPI()

        MainWindow.setObjectName("WeatherWindow")
        MainWindow.resize(600, 450)
        MainWindow.setMinimumSize(QtCore.QSize(600, 450))
        MainWindow.setMaximumSize(QtCore.QSize(600, 450))
        font = QtGui.QFont()
        font.setFamily("Tahoma")
        font.setPointSize(10)
        MainWindow.setFont(font)

        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")

        # ---------- Search Bar ----------
        self.groupBox = QtWidgets.QGroupBox(self.centralwidget)
        self.groupBox.setGeometry(QtCore.QRect(10, 10, 580, 70))
        self.groupBox.setTitle("Search")

        self.horizontalLayoutWidget = QtWidgets.QWidget(self.groupBox)
        self.horizontalLayoutWidget.setGeometry(QtCore.QRect(10, 25, 560, 35))
        self.horizontalLayout = QtWidgets.QHBoxLayout(self.horizontalLayoutWidget)
        self.horizontalLayout.setContentsMargins(0, 0, 0, 0)

        self.labelCity = QtWidgets.QLabel(self.horizontalLayoutWidget)
        self.labelCity.setText("City:")
        self.horizontalLayout.addWidget(self.labelCity)

        self.lineEditCity = QtWidgets.QLineEdit(self.horizontalLayoutWidget)
        self.lineEditCity.setPlaceholderText("Enter city name...")
        self.lineEditCity.setObjectName("lineEditCity")
        self.horizontalLayout.addWidget(self.lineEditCity)

        self.pushButtonSearch = QtWidgets.QPushButton(self.horizontalLayoutWidget)
        self.pushButtonSearch.setText("Search")
        self.pushButtonSearch.setMinimumSize(QtCore.QSize(120, 0))
        self.pushButtonSearch.setObjectName("pushButtonSearch")
        self.horizontalLayout.addWidget(self.pushButtonSearch)

        # ---------- Result Area ----------
        self.groupBoxResult = QtWidgets.QGroupBox(self.centralwidget)
        self.groupBoxResult.setGeometry(QtCore.QRect(10, 90, 580, 300))
        self.groupBoxResult.setTitle("Weather")

        self.labelCityName = QtWidgets.QLabel(self.groupBoxResult)
        self.labelCityName.setGeometry(QtCore.QRect(20, 35, 540, 35))
        f = QtGui.QFont()
        f.setPointSize(18)
        f.setBold(True)
        f.setWeight(75)
        self.labelCityName.setFont(f)
        self.labelCityName.setText("—")
        self.labelCityName.setAlignment(QtCore.Qt.AlignCenter)

        self.labelDesc = QtWidgets.QLabel(self.groupBoxResult)
        self.labelDesc.setGeometry(QtCore.QRect(20, 75, 540, 25))
        f2 = QtGui.QFont()
        f2.setPointSize(12)
        f2.setItalic(True)
        self.labelDesc.setFont(f2)
        self.labelDesc.setText("—")
        self.labelDesc.setAlignment(QtCore.Qt.AlignCenter)

        self.gridLayoutWidget = QtWidgets.QWidget(self.groupBoxResult)
        self.gridLayoutWidget.setGeometry(QtCore.QRect(40, 120, 500, 160))
        self.gridLayout = QtWidgets.QGridLayout(self.gridLayoutWidget)
        self.gridLayout.setContentsMargins(0, 0, 0, 0)
        self.gridLayout.setHorizontalSpacing(20)
        self.gridLayout.setVerticalSpacing(12)

        self.labels = {}
        fields = [
            ("Temp",       "—",  "°C"),
            ("Feels like", "—",  "°C"),
            ("Humidity",   "—",  "%"),
            ("Wind",       "—",  "m/s"),
            ("Pressure",   "—",  "hPa"),
            ("Country",    "—",  ""),
        ]
        for row, (key, default, unit) in enumerate(fields):
            lblKey = QtWidgets.QLabel(self.gridLayoutWidget)
            fk = QtGui.QFont()
            fk.setBold(True)
            lblKey.setFont(fk)
            lblKey.setText(f"{key}:")

            lblVal = QtWidgets.QLabel(self.gridLayoutWidget)
            lblVal.setText(f"{default} {unit}".strip())
            lblVal.setObjectName(f"label_{key}")

            self.gridLayout.addWidget(lblKey, row, 0)
            self.gridLayout.addWidget(lblVal, row, 1)
            self.labels[key] = (lblVal, unit)

        # ---------- Status Bar ----------
        MainWindow.setCentralWidget(self.centralwidget)

        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)
        self.statusbar.showMessage("Ready")

        # ---------- Signals ----------
        self.pushButtonSearch.clicked.connect(self.search)
        self.lineEditCity.returnPressed.connect(self.search)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle("Weather App")

    def search(self):
        city = self.lineEditCity.text().strip()
        if not city:
            QtWidgets.QMessageBox.warning(
                self.MainWindow, "Warning", "Please enter a city name"
            )
            return

        self.statusbar.showMessage(f"Searching for {city}...")
        QtWidgets.QApplication.processEvents()

        coords = self.api.get_coords(city)
        if not coords:
            self.statusbar.showMessage("City not found")
            QtWidgets.QMessageBox.warning(
                self.MainWindow, "Error", f"City '{city}' not found"
            )
            return

        data = self.api.get_weather(coords["lat"], coords["lon"])
        if not data:
            self.statusbar.showMessage("Weather data not available")
            QtWidgets.QMessageBox.warning(
                self.MainWindow, "Error", "Failed to get weather data"
            )
            return

        self.showWeather(data, coords)
        self.statusbar.showMessage(f"Last update: {city}")

    def showWeather(self, data, coords):
        name = coords.get("name", "—")
        country = coords.get("country", "—")
        self.labelCityName.setText(f"{name}, {country}")

        weather_list = data.get("weather", [])
        desc = weather_list[0].get("description", "—") if weather_list else "—"
        self.labelDesc.setText(desc.title())

        main = data.get("main", {})
        wind = data.get("wind", {})
        sys_data = data.get("sys", {})

        self._setValue("Temp",       main.get("temp"))
        self._setValue("Feels like", main.get("feels_like"))
        self._setValue("Humidity",   main.get("humidity"))
        self._setValue("Wind",       wind.get("speed"))
        self._setValue("Pressure",   main.get("pressure"))
        self._setValue("Country",    sys_data.get("country", country))

    def _setValue(self, key, value):
        lbl, unit = self.labels[key]
        if value is None:
            lbl.setText(f"— {unit}".strip())
        else:
            if isinstance(value, float):
                lbl.setText(f"{value:.1f} {unit}".strip())
            else:
                lbl.setText(f"{value} {unit}".strip())


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = Ui_WeatherWindow()
    ui.setupUi(MainWindow)
    MainWindow.show()
    sys.exit(app.exec_())